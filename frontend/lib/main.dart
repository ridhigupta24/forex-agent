import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const ForexApp());
}

// ─── App Root ────────────────────────────────────────────────────────────────

class ForexApp extends StatelessWidget {
  const ForexApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Forex Dashboard',
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
// Simulates login — pick a user to see their personalized dashboard

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
                      builder: (_) => DashboardScreen(userId: user['id']!),
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
        setState(() {
          error = 'Failed to load dashboard';
          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Cannot connect to server: $e';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        title: const Text('Dashboard',
            style: TextStyle(color: Color(0xFF00D4AA))),
        iconTheme: const IconThemeData(color: Color(0xFF00D4AA)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() => loading = true);
              fetchDashboard();
            },
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
              ? Center(child: Text(error!, style: const TextStyle(color: Colors.red)))
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
          // Header
          Padding(
            padding: const EdgeInsets.only(bottom: 16),
            child: Text(
              'Good day, ${widget.userId} 👋',
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          // Render each component
          ...components.map((component) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _buildComponent(component as Map<String, dynamic>),
            );
          }),
        ],
      ),
    );
  }

  // ─── Component Renderer ───────────────────────────────────────────────────
  // This is the core of SDUI — reads component type and renders the right widget

  Widget _buildComponent(Map<String, dynamic> component) {
    switch (component['type']) {
      case 'price_card':
        return PriceCard(data: component);
      case 'sentiment_widget':
        return SentimentWidget(data: component);
      case 'history_chart':
        return HistoryChart(data: component);
      case 'alert_banner':
        return AlertBanner(data: component);
      case 'trading_strategy':
        return TradingStrategy(data: component);
      case 'user_profile_card':
        return UserProfileCard(data: component);
      default:
        return const SizedBox.shrink();
    }
  }
}

// ─── Components ───────────────────────────────────────────────────────────────

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
              Text(
                data['pair'] ?? '',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF00D4AA),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                data['source'] ?? '',
                style: const TextStyle(fontSize: 12, color: Colors.white38),
              ),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                data['price']?.toString() ?? 'N/A',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Text(
                'Live Price',
                style: TextStyle(fontSize: 12, color: Colors.white38),
              ),
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
              Text(
                '${data['pair']} Sentiment',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
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
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Score bar
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
          Text(
            '${data['pair']} — 7 Day History',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
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
              Text(
                'Low: ${minPrice.toStringAsFixed(4)}',
                style: const TextStyle(fontSize: 11, color: Colors.redAccent),
              ),
              Text(
                'High: ${maxPrice.toStringAsFixed(4)}',
                style: const TextStyle(
                    fontSize: 11, color: Color(0xFF00D4AA)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// Simple line chart painter
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
            child: Text(
              data['message'] ?? '',
              style: TextStyle(color: severityColor, fontSize: 14),
            ),
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
              const Icon(Icons.auto_graph, color: Color(0xFF00D4AA), size: 20),
              const SizedBox(width: 8),
              Text(
                '${data['pair']} Strategy',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
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
              const Text(
                'Your Profile',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
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
                fontWeight: FontWeight.w500,
              )),
        ],
      ),
    );
  }
}