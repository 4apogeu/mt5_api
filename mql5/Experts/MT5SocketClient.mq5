//+------------------------------------------------------------------+
//|                                              MT5SocketClient.mq5 |
//|                                     MT5-Python Socket Bridge EA  |
//|                              Connects to Python server as client |
//+------------------------------------------------------------------+
#property copyright "MT5-Python Bridge"
#property version   "1.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\AccountInfo.mqh>

//--- Input parameters
input string   ServerAddress = "192.168.1.100";  // Python server IP
input int      ServerPort = 1111;                 // Python server port
input int      ReconnectDelayMs = 5000;           // Reconnect delay (ms)
input int      HeartbeatIntervalMs = 10000;       // Heartbeat interval (ms)
input int      TimerIntervalMs = 100;             // Polling interval (ms)

//--- Global variables
int            g_socket = INVALID_HANDLE;
bool           g_connected = false;
datetime       g_lastHeartbeat = 0;
string         g_receiveBuffer = "";
CTrade         g_trade;
CPositionInfo  g_position;
CAccountInfo   g_account;

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("MT5SocketClient initializing...");
    Print("Server: ", ServerAddress, ":", ServerPort);

    // Set up trade object
    g_trade.SetExpertMagicNumber(0);
    g_trade.SetDeviationInPoints(10);
    g_trade.SetTypeFilling(ORDER_FILLING_IOC);

    // Start timer for polling
    EventSetMillisecondTimer(TimerIntervalMs);

    // Attempt initial connection
    ConnectToServer();

    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
    Disconnect();
    Print("MT5SocketClient stopped. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Timer function - main polling loop                                 |
//+------------------------------------------------------------------+
void OnTimer()
{
    // Check connection status
    if(!g_connected)
    {
        ConnectToServer();
        return;
    }

    // Read incoming data
    ReadFromSocket();

    // Process complete messages
    ProcessMessages();

    // Send heartbeat if needed
    CheckHeartbeat();
}

//+------------------------------------------------------------------+
//| Connect to Python server                                           |
//+------------------------------------------------------------------+
bool ConnectToServer()
{
    if(g_connected)
        return true;

    // Create socket
    g_socket = SocketCreate();
    if(g_socket == INVALID_HANDLE)
    {
        Print("Failed to create socket. Error: ", GetLastError());
        return false;
    }

    // Connect to server
    if(!SocketConnect(g_socket, ServerAddress, ServerPort, 5000))
    {
        Print("Failed to connect to ", ServerAddress, ":", ServerPort, ". Error: ", GetLastError());
        SocketClose(g_socket);
        g_socket = INVALID_HANDLE;
        Sleep(ReconnectDelayMs);
        return false;
    }

    g_connected = true;
    g_lastHeartbeat = TimeCurrent();
    g_receiveBuffer = "";
    Print("Connected to Python server at ", ServerAddress, ":", ServerPort);

    return true;
}

//+------------------------------------------------------------------+
//| Disconnect from server                                             |
//+------------------------------------------------------------------+
void Disconnect()
{
    if(g_socket != INVALID_HANDLE)
    {
        SocketClose(g_socket);
        g_socket = INVALID_HANDLE;
    }
    g_connected = false;
    g_receiveBuffer = "";
    Print("Disconnected from server");
}

//+------------------------------------------------------------------+
//| Read data from socket into buffer                                  |
//+------------------------------------------------------------------+
void ReadFromSocket()
{
    if(!g_connected || g_socket == INVALID_HANDLE)
        return;

    uchar data[];
    int bytesRead = SocketRead(g_socket, data, 4096, 10);

    if(bytesRead < 0)
    {
        int error = GetLastError();
        if(error != 0 && error != 4014) // 4014 = timeout, which is normal
        {
            Print("Socket read error: ", error);
            Disconnect();
        }
        return;
    }

    if(bytesRead > 0)
    {
        g_receiveBuffer += CharArrayToString(data, 0, bytesRead);
    }
}

//+------------------------------------------------------------------+
//| Process complete messages in buffer                                |
//+------------------------------------------------------------------+
void ProcessMessages()
{
    int pos;
    while((pos = StringFind(g_receiveBuffer, "\n")) >= 0)
    {
        string message = StringSubstr(g_receiveBuffer, 0, pos);
        g_receiveBuffer = StringSubstr(g_receiveBuffer, pos + 1);

        if(StringLen(message) > 0)
        {
            HandleMessage(message);
        }
    }
}

//+------------------------------------------------------------------+
//| Handle a single JSON message                                       |
//+------------------------------------------------------------------+
void HandleMessage(string json)
{
    // Parse JSON fields
    string requestId = GetJsonString(json, "id");
    string action = GetJsonString(json, "action");
    string params = GetJsonObject(json, "params");

    Print("Received: ", action, " [", requestId, "]");

    string response = "";

    if(action == "TRADE")
        response = HandleTrade(requestId, params);
    else if(action == "GET_DATA")
        response = HandleGetData(requestId, params);
    else if(action == "GET_TICK")
        response = HandleGetTick(requestId, params);
    else if(action == "GET_ACCOUNT")
        response = HandleGetAccount(requestId);
    else if(action == "GET_POSITIONS")
        response = HandleGetPositions(requestId);
    else if(action == "CLOSE_POSITION")
        response = HandleClosePosition(requestId, params);
    else if(action == "HEARTBEAT")
        response = HandleHeartbeat(requestId);
    else
        response = BuildErrorResponse(requestId, -1, "Unknown action: " + action);

    SendResponse(response);
}

//+------------------------------------------------------------------+
//| Handle TRADE command                                               |
//+------------------------------------------------------------------+
string HandleTrade(string requestId, string params)
{
    string symbol = GetJsonString(params, "symbol");
    string typeStr = GetJsonString(params, "type");
    double volume = GetJsonDouble(params, "volume");
    double sl = GetJsonDouble(params, "sl");
    double tp = GetJsonDouble(params, "tp");
    double price = GetJsonDouble(params, "price");
    int magic = (int)GetJsonDouble(params, "magic");
    string comment = GetJsonString(params, "comment");

    // Validate symbol
    if(!SymbolSelect(symbol, true))
    {
        return BuildErrorResponse(requestId, GetLastError(), "Invalid symbol: " + symbol);
    }

    // Get current prices
    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick))
    {
        return BuildErrorResponse(requestId, GetLastError(), "Failed to get tick for " + symbol);
    }

    // Set magic number
    if(magic > 0)
        g_trade.SetExpertMagicNumber(magic);

    // Determine order type and execute
    ENUM_ORDER_TYPE orderType;
    double execPrice;
    bool result = false;

    if(typeStr == "BUY")
    {
        execPrice = tick.ask;
        result = g_trade.Buy(volume, symbol, execPrice, sl, tp, comment);
    }
    else if(typeStr == "SELL")
    {
        execPrice = tick.bid;
        result = g_trade.Sell(volume, symbol, execPrice, sl, tp, comment);
    }
    else if(typeStr == "BUY_LIMIT")
    {
        result = g_trade.BuyLimit(volume, price, symbol, sl, tp, ORDER_TIME_GTC, 0, comment);
    }
    else if(typeStr == "SELL_LIMIT")
    {
        result = g_trade.SellLimit(volume, price, symbol, sl, tp, ORDER_TIME_GTC, 0, comment);
    }
    else if(typeStr == "BUY_STOP")
    {
        result = g_trade.BuyStop(volume, price, symbol, sl, tp, ORDER_TIME_GTC, 0, comment);
    }
    else if(typeStr == "SELL_STOP")
    {
        result = g_trade.SellStop(volume, price, symbol, sl, tp, ORDER_TIME_GTC, 0, comment);
    }
    else
    {
        return BuildErrorResponse(requestId, -1, "Unknown order type: " + typeStr);
    }

    if(!result)
    {
        return BuildErrorResponse(requestId, (int)g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
    }

    // Build success response
    string data = StringFormat(
        "{\"ticket\":%d,\"price_executed\":%.5f,\"volume_executed\":%.2f}",
        g_trade.ResultDeal(),
        g_trade.ResultPrice(),
        g_trade.ResultVolume()
    );

    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Handle GET_DATA command                                            |
//+------------------------------------------------------------------+
string HandleGetData(string requestId, string params)
{
    string symbol = GetJsonString(params, "symbol");
    string tfStr = GetJsonString(params, "timeframe");
    int count = (int)GetJsonDouble(params, "count");

    // Validate symbol
    if(!SymbolSelect(symbol, true))
    {
        return BuildErrorResponse(requestId, GetLastError(), "Invalid symbol: " + symbol);
    }

    // Map timeframe string to enum
    ENUM_TIMEFRAMES timeframe = StringToTimeframe(tfStr);
    if(timeframe == PERIOD_CURRENT)
    {
        return BuildErrorResponse(requestId, -1, "Invalid timeframe: " + tfStr);
    }

    // Get rates
    MqlRates rates[];
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(symbol, timeframe, 0, count, rates);

    if(copied <= 0)
    {
        return BuildErrorResponse(requestId, GetLastError(), "Failed to copy rates");
    }

    // Build rates array JSON
    string ratesJson = "[";
    for(int i = 0; i < copied; i++)
    {
        if(i > 0) ratesJson += ",";
        ratesJson += StringFormat(
            "{\"time\":\"%s\",\"open\":%.5f,\"high\":%.5f,\"low\":%.5f,\"close\":%.5f,\"volume\":%d}",
            TimeToString(rates[i].time, TIME_DATE|TIME_SECONDS),
            rates[i].open,
            rates[i].high,
            rates[i].low,
            rates[i].close,
            rates[i].tick_volume
        );
    }
    ratesJson += "]";

    string data = "{\"rates\":" + ratesJson + "}";
    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Handle GET_TICK command                                            |
//+------------------------------------------------------------------+
string HandleGetTick(string requestId, string params)
{
    string symbol = GetJsonString(params, "symbol");

    // Validate symbol
    if(!SymbolSelect(symbol, true))
    {
        return BuildErrorResponse(requestId, GetLastError(), "Invalid symbol: " + symbol);
    }

    MqlTick tick;
    if(!SymbolInfoTick(symbol, tick))
    {
        return BuildErrorResponse(requestId, GetLastError(), "Failed to get tick");
    }

    string data = StringFormat(
        "{\"bid\":%.5f,\"ask\":%.5f,\"last\":%.5f,\"volume\":%d,\"time\":\"%s\"}",
        tick.bid,
        tick.ask,
        tick.last,
        tick.volume,
        TimeToString(tick.time, TIME_DATE|TIME_SECONDS)
    );

    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Handle GET_ACCOUNT command                                         |
//+------------------------------------------------------------------+
string HandleGetAccount(string requestId)
{
    string data = StringFormat(
        "{\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,\"free_margin\":%.2f,\"leverage\":%d}",
        g_account.Balance(),
        g_account.Equity(),
        g_account.Margin(),
        g_account.FreeMargin(),
        g_account.Leverage()
    );

    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Handle GET_POSITIONS command                                       |
//+------------------------------------------------------------------+
string HandleGetPositions(string requestId)
{
    string positionsJson = "[";
    bool first = true;

    for(int i = 0; i < PositionsTotal(); i++)
    {
        if(g_position.SelectByIndex(i))
        {
            if(!first) positionsJson += ",";
            first = false;

            string posType = (g_position.PositionType() == POSITION_TYPE_BUY) ? "BUY" : "SELL";

            positionsJson += StringFormat(
                "{\"ticket\":%d,\"symbol\":\"%s\",\"type\":\"%s\",\"volume\":%.2f,\"open_price\":%.5f,\"sl\":%.5f,\"tp\":%.5f,\"profit\":%.2f}",
                g_position.Ticket(),
                g_position.Symbol(),
                posType,
                g_position.Volume(),
                g_position.PriceOpen(),
                g_position.StopLoss(),
                g_position.TakeProfit(),
                g_position.Profit()
            );
        }
    }
    positionsJson += "]";

    string data = "{\"positions\":" + positionsJson + "}";
    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Handle CLOSE_POSITION command                                      |
//+------------------------------------------------------------------+
string HandleClosePosition(string requestId, string params)
{
    ulong ticket = (ulong)GetJsonDouble(params, "ticket");

    if(!g_position.SelectByTicket(ticket))
    {
        return BuildErrorResponse(requestId, GetLastError(), "Position not found: " + IntegerToString(ticket));
    }

    double closePrice = (g_position.PositionType() == POSITION_TYPE_BUY)
                        ? SymbolInfoDouble(g_position.Symbol(), SYMBOL_BID)
                        : SymbolInfoDouble(g_position.Symbol(), SYMBOL_ASK);

    double profit = g_position.Profit();

    if(!g_trade.PositionClose(ticket))
    {
        return BuildErrorResponse(requestId, (int)g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
    }

    string data = StringFormat(
        "{\"close_price\":%.5f,\"profit\":%.2f}",
        closePrice,
        profit
    );

    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Handle HEARTBEAT command                                           |
//+------------------------------------------------------------------+
string HandleHeartbeat(string requestId)
{
    g_lastHeartbeat = TimeCurrent();

    string data = StringFormat(
        "{\"timestamp\":\"%s\",\"connected\":true}",
        TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS)
    );

    return BuildSuccessResponse(requestId, data);
}

//+------------------------------------------------------------------+
//| Check and send heartbeat if needed                                 |
//+------------------------------------------------------------------+
void CheckHeartbeat()
{
    if(TimeCurrent() - g_lastHeartbeat > HeartbeatIntervalMs / 1000)
    {
        // Just update the timestamp - heartbeat is initiated by Python
        g_lastHeartbeat = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Send response to Python server                                     |
//+------------------------------------------------------------------+
void SendResponse(string response)
{
    if(!g_connected || g_socket == INVALID_HANDLE)
        return;

    response += "\n";  // Add message terminator

    uchar data[];
    int len = StringToCharArray(response, data, 0, WHOLE_ARRAY, CP_UTF8);

    // Remove null terminator from length
    if(len > 0) len--;

    int sent = SocketSend(g_socket, data, len);
    if(sent < 0)
    {
        Print("Failed to send response. Error: ", GetLastError());
        Disconnect();
    }
}

//+------------------------------------------------------------------+
//| Build success response JSON                                        |
//+------------------------------------------------------------------+
string BuildSuccessResponse(string requestId, string data)
{
    return StringFormat(
        "{\"id\":\"%s\",\"success\":true,\"error_code\":0,\"error_message\":\"\",\"data\":%s}",
        requestId,
        data
    );
}

//+------------------------------------------------------------------+
//| Build error response JSON                                          |
//+------------------------------------------------------------------+
string BuildErrorResponse(string requestId, int errorCode, string errorMessage)
{
    // Escape quotes in error message
    StringReplace(errorMessage, "\"", "\\\"");

    return StringFormat(
        "{\"id\":\"%s\",\"success\":false,\"error_code\":%d,\"error_message\":\"%s\",\"data\":{}}",
        requestId,
        errorCode,
        errorMessage
    );
}

//+------------------------------------------------------------------+
//| Convert timeframe string to enum                                   |
//+------------------------------------------------------------------+
ENUM_TIMEFRAMES StringToTimeframe(string tf)
{
    if(tf == "M1")  return PERIOD_M1;
    if(tf == "M5")  return PERIOD_M5;
    if(tf == "M15") return PERIOD_M15;
    if(tf == "M30") return PERIOD_M30;
    if(tf == "H1")  return PERIOD_H1;
    if(tf == "H4")  return PERIOD_H4;
    if(tf == "D1")  return PERIOD_D1;
    if(tf == "W1")  return PERIOD_W1;
    if(tf == "MN1") return PERIOD_MN1;
    return PERIOD_CURRENT;  // Invalid
}

//+------------------------------------------------------------------+
//| Simple JSON string value parser                                    |
//+------------------------------------------------------------------+
string GetJsonString(string json, string key)
{
    string searchKey = "\"" + key + "\":\"";
    int start = StringFind(json, searchKey);
    if(start < 0) return "";

    start += StringLen(searchKey);
    int end = StringFind(json, "\"", start);
    if(end < 0) return "";

    return StringSubstr(json, start, end - start);
}

//+------------------------------------------------------------------+
//| Simple JSON number value parser                                    |
//+------------------------------------------------------------------+
double GetJsonDouble(string json, string key)
{
    // Try quoted number first
    string searchKey = "\"" + key + "\":\"";
    int start = StringFind(json, searchKey);
    if(start >= 0)
    {
        start += StringLen(searchKey);
        int end = StringFind(json, "\"", start);
        if(end > start)
            return StringToDouble(StringSubstr(json, start, end - start));
    }

    // Try unquoted number
    searchKey = "\"" + key + "\":";
    start = StringFind(json, searchKey);
    if(start < 0) return 0;

    start += StringLen(searchKey);

    // Skip whitespace
    while(start < StringLen(json) && (StringGetCharacter(json, start) == ' '))
        start++;

    // Find end of number
    int end = start;
    while(end < StringLen(json))
    {
        ushort c = StringGetCharacter(json, end);
        if(c != '-' && c != '.' && (c < '0' || c > '9'))
            break;
        end++;
    }

    if(end > start)
        return StringToDouble(StringSubstr(json, start, end - start));

    return 0;
}

//+------------------------------------------------------------------+
//| Simple JSON object value parser                                    |
//+------------------------------------------------------------------+
string GetJsonObject(string json, string key)
{
    string searchKey = "\"" + key + "\":";
    int start = StringFind(json, searchKey);
    if(start < 0) return "{}";

    start += StringLen(searchKey);

    // Skip whitespace
    while(start < StringLen(json) && StringGetCharacter(json, start) == ' ')
        start++;

    if(StringGetCharacter(json, start) != '{')
        return "{}";

    // Find matching closing brace
    int depth = 0;
    int end = start;
    while(end < StringLen(json))
    {
        ushort c = StringGetCharacter(json, end);
        if(c == '{') depth++;
        if(c == '}') depth--;
        end++;
        if(depth == 0) break;
    }

    return StringSubstr(json, start, end - start);
}

//+------------------------------------------------------------------+
//| OnTick - not used for socket communication                         |
//+------------------------------------------------------------------+
void OnTick()
{
    // Socket communication handled in OnTimer
}
//+------------------------------------------------------------------+
