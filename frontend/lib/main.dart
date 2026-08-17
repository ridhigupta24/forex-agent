import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';

void main() {
  runApp(const ForexApp());
}

// ─── App Root ────────────────────────────────────────────────────────────────

class ForexApp extends StatelessWidget {
  const ForexApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Forex AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00D4AA),
          secondary: Color(0xFF1F6FEB),
          surface: Color(0xFF161B22),
        ),
      ),
      home: const UserSelectScreen(),
    );
  }
}

// ─── User Select Screen ───────────────────────────────────────────────────────

class UserSelectScreen extends StatelessWidget {
  const UserSelectScreen({super.key});

  final List<Map<String, String>> users = const [
    {'id': 'user-conservative', 'label': 'Conservative Trader', 'icon': '🛡️'},
    {'id': 'test-user-123', 'label': 'Moderate Trader', 'icon': '📊'},
    {'id': 'user-aggressive', 'label': 'Aggressive Trader', 'icon': '🔥'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 48),
              const Text(
                'Forex AI',
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF00D4AA),
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'Select your profile to see your\npersonalized dashboard',
                style: TextStyle(fontSize: 16, color: Colors.white60),
              ),
              const SizedBox(height: 48),
              ...users.map((user) => Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: GestureDetector(
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => MainScreen(userId: user['id']!),
                    ),
                  ),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: const Color(0xFF161B22),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFF30363D)),
                    ),
                    child: Row(
                      children: [
                        Text(user['icon']!, style: const TextStyle(fontSize: 32)),
                        const SizedBox(width: 16),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user['label']!,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              user['id']!,
                              style: const TextStyle(
                                fontSize: 12,
                                color: Colors.white38,
                              ),
                            ),
                          ],
                        ),
                        const Spacer(),
                        const Icon(Icons.arrow_forward_ios,
                            color: Color(0xFF00D4AA), size: 16),
                      ],
                    ),
                  ),
                ),
              )),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Main Screen with Bottom Nav ─────────────────────────────────────────────

class MainScreen extends StatefulWidget {
  final String userId;
  const MainScreen({super.key, required this.userId});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          DashboardScreen(userId: widget.userId),
          ChatScreen(userId: widget.userId),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        backgroundColor: const Color(0xFF161B22),
        selectedItemColor: const Color(0xFF00D4AA),
        unselectedItemColor: Colors.white38,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_rounded),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_rounded),
            label: 'Chat',
          ),
        ],
      ),
    );
  }
}

// ─── Dashboard Screen ─────────────────────────────────────────────────────────

class DashboardScreen extends StatefulWidget {
  final String userId;
  const DashboardScreen({super.key, required this.userId});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? screenData;
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    fetchDashboard();
  }

  Future<void> fetchDashboard() async {
    setState(() { loading = true; error = null; });
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/ui/dashboard?user_id=${widget.userId}'),
      );
      if (response.statusCode == 200) {
        setState(() {
          screenData = json.decode(response.body);
          loading = false;
        });
      } else {
        setState(() { error = 'Failed to load dashboard'; loading = false; });
      }
    } catch (e) {
      setState(() { error = 'Cannot connect to server: $e'; loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        automaticallyImplyLeading: false,
        title: const Text('Dashboard',
            style: TextStyle(color: Color(0xFF00D4AA))),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF00D4AA)),
            onPressed: fetchDashboard,
          )
        ],
      ),
      body: loading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Color(0xFF00D4AA)),
                  SizedBox(height: 16),
                  Text('AI is personalizing your dashboard...',
                      style: TextStyle(color: Colors.white60)),
                ],
              ),
            )
          : error != null
              ? Center(child: Text(error!, style: const TextStyle(color: Colors.redAccent)))
              : _buildDashboard(),
    );
  }

  Widget _buildDashboard() {
    final components = screenData!['components'] as List<dynamic>;
    return RefreshIndicator(
      onRefresh: fetchDashboard,
      color: const Color(0xFF00D4AA),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(
              'Good day, ${widget.userId} 👋',
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
          ),
          ...components.map((component) => Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: _buildComponent(component as Map<String, dynamic>),
          )),
        ],
      ),
    );
  }

  Widget _buildComponent(Map<String, dynamic> component) {
    switch (component['type']) {
      case 'price_card': return PriceCard(data: component);
      case 'sentiment_widget': return SentimentWidget(data: component);
      case 'history_chart': return HistoryChart(data: component);
      case 'alert_banner': return AlertBanner(data: component);
      case 'trading_strategy': return TradingStrategy(data: component);
      case 'user_profile_card': return UserProfileCard(data: component);
      default: return const SizedBox.shrink();
    }
  }
}

// ─── Chat Screen ──────────────────────────────────────────────────────────────

class ChatMessage {
  final String text;
  final bool isUser;
  final bool isToolCall;
  final bool isStreaming;

  ChatMessage({
    required this.text,
    required this.isUser,
    this.isToolCall = false,
    this.isStreaming = false,
  });
}

class ChatScreen extends StatefulWidget {
  final String userId;
  const ChatScreen({super.key, required this.userId});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = [];
  WebSocketChannel? _channel;
  bool _isConnected = false;
  bool _isThinking = false;

  @override
  void initState() {
    super.initState();
    _connect();
  }

  void _connect() {
    try {
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://localhost:8000/ws?user_id=${widget.userId}'),
      );
      setState(() => _isConnected = true);

      _channel!.stream.listen(
        (data) => _handleMessage(data),
        onDone: () {
          setState(() => _isConnected = false);
        },
        onError: (error) {
          setState(() => _isConnected = false);
        },
      );
    } catch (e) {
      setState(() => _isConnected = false);
    }
  }

  void _handleMessage(dynamic data) {
    final message = json.decode(data as String);
    final type = message['type'] as String?;

    setState(() {
      switch (type) {
        case 'thinking':
          _isThinking = true;
          break;

        case 'tool_call':
          // Show tool call as a small indicator bubble
          _messages.add(ChatMessage(
            text: '🔧 ${message['tool']}',
            isUser: false,
            isToolCall: true,
          ));
          break;

        case 'token':
          // Append token to the last AI message or create new one
          final token = message['token'] as String? ?? '';
          if (_messages.isNotEmpty &&
              !_messages.last.isUser &&
              !_messages.last.isToolCall &&
              _messages.last.isStreaming) {
            final last = _messages.removeLast();
            _messages.add(ChatMessage(
              text: last.text + token,
              isUser: false,
              isStreaming: true,
            ));
          } else {
            _isThinking = false;
            _messages.add(ChatMessage(
              text: token,
              isUser: false,
              isStreaming: true,
            ));
          }
          break;

        case 'done':
          _isThinking = false;
          // Mark last message as no longer streaming
          if (_messages.isNotEmpty && _messages.last.isStreaming) {
            final last = _messages.removeLast();
            _messages.add(ChatMessage(
              text: last.text.isEmpty
                  ? (message['response'] as String? ?? '')
                  : last.text,
              isUser: false,
              isStreaming: false,
            ));
          } else if (message['is_fast_path'] == true) {
            _isThinking = false;
            _messages.add(ChatMessage(
              text: message['response'] as String? ?? '',
              isUser: false,
            ));
          }
          break;

        case 'error':
          _isThinking = false;
          _messages.add(ChatMessage(
            text: '❌ ${message['response']}',
            isUser: false,
          ));
          break;
      }
    });

    _scrollToBottom();
  }

  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isEmpty || !_isConnected) return;

    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true));
      _isThinking = true;
    });

    _channel?.sink.add(json.encode({'message': text}));
    _controller.clear();
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _channel?.sink.close();
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        automaticallyImplyLeading: false,
        title: Row(
          children: [
            const Text('Forex AI Chat',
                style: TextStyle(color: Color(0xFF00D4AA))),
            const Spacer(),
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: _isConnected ? const Color(0xFF00D4AA) : Colors.redAccent,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
            Text(
              _isConnected ? 'Connected' : 'Disconnected',
              style: TextStyle(
                fontSize: 12,
                color: _isConnected ? const Color(0xFF00D4AA) : Colors.redAccent,
              ),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          // Messages list
          Expanded(
            child: _messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length + (_isThinking ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _messages.length && _isThinking) {
                        return _buildThinkingIndicator();
                      }
                      return _buildMessageBubble(_messages[index]);
                    },
                  ),
          ),

          // Input bar
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              color: Color(0xFF161B22),
              border: Border(top: BorderSide(color: Color(0xFF30363D))),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: InputDecoration(
                      hintText: 'Ask about any forex pair...',
                      hintStyle: const TextStyle(color: Colors.white38),
                      filled: true,
                      fillColor: const Color(0xFF0D1117),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 12),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: _sendMessage,
                  child: Container(
                    width: 48,
                    height: 48,
                    decoration: const BoxDecoration(
                      color: Color(0xFF00D4AA),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.send_rounded,
                        color: Colors.black, size: 20),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.chat_bubble_outline_rounded,
              size: 64, color: Colors.white12),
          const SizedBox(height: 16),
          const Text('Ask me anything about forex',
              style: TextStyle(color: Colors.white38, fontSize: 16)),
          const SizedBox(height: 8),
          Text('Logged in as ${widget.userId}',
              style: const TextStyle(color: Colors.white24, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildThinkingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: const Color(0xFF161B22),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0xFF30363D)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Color(0xFF00D4AA),
                  ),
                ),
                const SizedBox(width: 8),
                const Text('Thinking...',
                    style: TextStyle(color: Colors.white38, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    // Tool call indicator — small pill
    if (message.isToolCall) {
      return Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: const Color(0xFF1F6FEB).withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: const Color(0xFF1F6FEB).withOpacity(0.3)),
              ),
              child: Text(
                message.text,
                style: const TextStyle(
                    color: Color(0xFF1F6FEB), fontSize: 11),
              ),
            ),
          ],
        ),
      );
    }

    // User or AI message bubble
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: message.isUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!message.isUser) ...[
            Container(
              width: 28,
              height: 28,
              margin: const EdgeInsets.only(right: 8),
              decoration: const BoxDecoration(
                color: Color(0xFF00D4AA),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.auto_awesome,
                  size: 14, color: Colors.black),
            ),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: message.isUser
                    ? const Color(0xFF00D4AA).withOpacity(0.15)
                    : const Color(0xFF161B22),
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(18),
                  topRight: const Radius.circular(18),
                  bottomLeft: Radius.circular(message.isUser ? 18 : 4),
                  bottomRight: Radius.circular(message.isUser ? 4 : 18),
                ),
                border: Border.all(
                  color: message.isUser
                      ? const Color(0xFF00D4AA).withOpacity(0.3)
                      : const Color(0xFF30363D),
                ),
              ),
              child: message.isUser
                  ? Text(
                      message.text,
                      style: const TextStyle(
                        color: Color(0xFF00D4AA),
                        fontSize: 14,
                        height: 1.5,
                      ),
                    )
                  : MarkdownBody(
                      data: message.text,
                      styleSheet: MarkdownStyleSheet(
                        p: const TextStyle(
                            color: Colors.white, fontSize: 14, height: 1.5),
                        strong: const TextStyle(
                            color: Color(0xFF00D4AA),
                            fontWeight: FontWeight.bold,
                            fontSize: 14),
                        em: const TextStyle(
                            color: Colors.white70,
                            fontStyle: FontStyle.italic,
                            fontSize: 14),
                        listBullet: const TextStyle(
                            color: Color(0xFF00D4AA), fontSize: 14),
                        code: const TextStyle(
                            color: Color(0xFF00D4AA),
                            backgroundColor: Color(0xFF0D1117),
                            fontSize: 13),
                        blockquote: const TextStyle(
                            color: Colors.white60, fontSize: 14),
                        h1: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold),
                        h2: const TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold),
                        h3: const TextStyle(
                            color: Color(0xFF00D4AA),
                            fontSize: 14,
                            fontWeight: FontWeight.bold),
                      ),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Dashboard Components ────────────────────────────────────────────────────

class PriceCard extends StatelessWidget {
  final Map<String, dynamic> data;
  const PriceCard({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1A3A4A), Color(0xFF161B22)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF00D4AA).withOpacity(0.3)),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(data['pair'] ?? '',
                  style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF00D4AA))),
              const SizedBox(height: 4),
              Text(data['source'] ?? '',
                  style: const TextStyle(fontSize: 12, color: Colors.white38)),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(data['price']?.toString() ?? 'N/A',
                  style: const TextStyle(
                      fontSize: 28, fontWeight: FontWeight.bold)),
              const Text('Live Price',
                  style: TextStyle(fontSize: 12, color: Colors.white38)),
            ],
          ),
        ],
      ),
    );
  }
}

class SentimentWidget extends StatelessWidget {
  final Map<String, dynamic> data;
  const SentimentWidget({super.key, required this.data});

  Color get sentimentColor {
    switch (data['sentiment']) {
      case 'bullish': return const Color(0xFF00D4AA);
      case 'bearish': return Colors.redAccent;
      default: return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    final signals = (data['signals'] as List<dynamic>?) ?? [];
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF30363D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('${data['pair']} Sentiment',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold)),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: sentimentColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: sentimentColor.withOpacity(0.5)),
                ),
                child: Text(
                  (data['sentiment'] ?? 'neutral').toUpperCase(),
                  style: TextStyle(
                      color: sentimentColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (data['score'] as num?)?.toDouble() ?? 0.5,
              backgroundColor: const Color(0xFF30363D),
              valueColor: AlwaysStoppedAnimation<Color>(sentimentColor),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 12),
          ...signals.map((signal) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              children: [
                Icon(Icons.circle, size: 6, color: sentimentColor),
                const SizedBox(width: 8),
                Text(signal.toString(),
                    style: const TextStyle(color: Colors.white70)),
              ],
            ),
          )),
        ],
      ),
    );
  }
}

class HistoryChart extends StatelessWidget {
  final Map<String, dynamic> data;
  const HistoryChart({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final chartData = (data['data'] as List<dynamic>?) ?? [];
    if (chartData.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFF161B22),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF30363D)),
        ),
        child: const Text('No history data available',
            style: TextStyle(color: Colors.white38)),
      );
    }

    final prices = chartData
        .map((d) => (d['price'] as num).toDouble())
        .toList();
    final minPrice = prices.reduce((a, b) => a < b ? a : b);
    final maxPrice = prices.reduce((a, b) => a > b ? a : b);
    final range = maxPrice - minPrice;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF30363D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('${data['pair']} — 7 Day History',
              style: const TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          SizedBox(
            height: 100,
            child: CustomPaint(
              size: Size.infinite,
              painter: LineChartPainter(
                prices: prices,
                minPrice: minPrice,
                range: range == 0 ? 1 : range,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Low: ${minPrice.toStringAsFixed(4)}',
                  style: const TextStyle(
                      fontSize: 11, color: Colors.redAccent)),
              Text('High: ${maxPrice.toStringAsFixed(4)}',
                  style: const TextStyle(
                      fontSize: 11, color: Color(0xFF00D4AA))),
            ],
          ),
        ],
      ),
    );
  }
}

class LineChartPainter extends CustomPainter {
  final List<double> prices;
  final double minPrice;
  final double range;

  LineChartPainter({
    required this.prices,
    required this.minPrice,
    required this.range,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF00D4AA)
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke;

    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          const Color(0xFF00D4AA).withOpacity(0.3),
          const Color(0xFF00D4AA).withOpacity(0.0),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.fill;

    if (prices.length < 2) return;

    final path = Path();
    final fillPath = Path();

    for (int i = 0; i < prices.length; i++) {
      final x = (i / (prices.length - 1)) * size.width;
      final y = size.height - ((prices[i] - minPrice) / range) * size.height;

      if (i == 0) {
        path.moveTo(x, y);
        fillPath.moveTo(x, size.height);
        fillPath.lineTo(x, y);
      } else {
        path.lineTo(x, y);
        fillPath.lineTo(x, y);
      }
    }

    fillPath.lineTo(size.width, size.height);
    fillPath.close();

    canvas.drawPath(fillPath, fillPaint);
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class AlertBanner extends StatelessWidget {
  final Map<String, dynamic> data;
  const AlertBanner({super.key, required this.data});

  Color get severityColor {
    switch (data['severity']) {
      case 'danger': return Colors.redAccent;
      case 'warning': return Colors.orange;
      default: return const Color(0xFF1F6FEB);
    }
  }

  IconData get severityIcon {
    switch (data['severity']) {
      case 'danger': return Icons.warning_rounded;
      case 'warning': return Icons.info_rounded;
      default: return Icons.lightbulb_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: severityColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: severityColor.withOpacity(0.4)),
      ),
      child: Row(
        children: [
          Icon(severityIcon, color: severityColor, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Text(data['message'] ?? '',
                style: TextStyle(color: severityColor, fontSize: 14)),
          ),
        ],
      ),
    );
  }
}

class TradingStrategy extends StatelessWidget {
  final Map<String, dynamic> data;
  const TradingStrategy({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final tips = (data['tips'] as List<dynamic>?) ?? [];
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF30363D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.auto_graph,
                  color: Color(0xFF00D4AA), size: 20),
              const SizedBox(width: 8),
              Text('${data['pair']} Strategy',
                  style: const TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 12),
          ...tips.map((tip) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('→ ',
                    style: TextStyle(color: Color(0xFF00D4AA))),
                Expanded(
                  child: Text(tip.toString(),
                      style: const TextStyle(color: Colors.white70)),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }
}

class UserProfileCard extends StatelessWidget {
  final Map<String, dynamic> data;
  const UserProfileCard({super.key, required this.data});

  Color get riskColor {
    switch (data['risk_tolerance']) {
      case 'high': return Colors.redAccent;
      case 'low': return const Color(0xFF00D4AA);
      default: return Colors.orange;
    }
  }

  @override
  Widget build(BuildContext context) {
    final pairs = (data['preferred_pairs'] as List<dynamic>?) ?? [];
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF161B22),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF30363D)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.person_rounded,
                  color: Color(0xFF00D4AA), size: 20),
              const SizedBox(width: 8),
              const Text('Your Profile',
                  style: TextStyle(
                      fontSize: 16, fontWeight: FontWeight.bold)),
            ],
          ),
          const SizedBox(height: 16),
          _profileRow('User ID', data['user_id'] ?? ''),
          _profileRow('Risk Tolerance',
              (data['risk_tolerance'] ?? '').toUpperCase(),
              valueColor: riskColor),
          _profileRow('Response Style', data['response_style'] ?? ''),
          _profileRow('Preferred Pairs', pairs.join(', ')),
        ],
      ),
    );
  }

  Widget _profileRow(String label, String value, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: const TextStyle(color: Colors.white38, fontSize: 13)),
          Text(value,
              style: TextStyle(
                  color: valueColor ?? Colors.white,
                  fontSize: 13,
                  fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}