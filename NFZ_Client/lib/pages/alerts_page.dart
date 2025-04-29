import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:nfz/config.dart';

class AlertPage extends StatefulWidget {
  @override
  _AlertPageState createState() => _AlertPageState();
}

class _AlertPageState extends State<AlertPage> {
  List<AlertMessage> alerts = [];
  final TextEditingController _controller = TextEditingController();
  String? username;

  final List<String> quickReplies = [
    "I received this too",
    "Looks like phishing",
    "Seems safe to me",
    "I reported it"
  ];

  @override
  void initState() {
    super.initState();
    _loadUsername();
    _fetchAlerts();
  }

  Future<void> _loadUsername() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      username = prefs.getString('username') ?? 'Unknown';
    });
  }

  Future<void> _fetchAlerts() async {
    try {
      final response = await http.get(Uri.parse('$serverUrl/chat_messages'));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        setState(() {
          alerts = data.map((e) => AlertMessage.fromJson(e)).toList().reversed.toList();
        });
      }
    } catch (e) {
      print("Error fetching alerts: $e");
    }
  }

  Future<void> _sendAlert(String text) async {
    if (text.trim().isEmpty || username == null) return;

    try {
      final response = await http.post(
        Uri.parse('$serverUrl/send_chat_message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'message': text}),
      );
      if (response.statusCode == 200) {
        _controller.clear();
        await _fetchAlerts();
      }
    } catch (e) {
      print("Error sending alert: $e");
    }
  }

  Widget _buildQuickReplies() {
    return Wrap(
      spacing: 8.0,
      children: quickReplies.map((reply) {
        return ActionChip(
          label: Text(reply),
          onPressed: () => _sendAlert(reply),
        );
      }).toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Community Alerts')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              reverse: true,
              itemCount: alerts.length,
              itemBuilder: (context, index) {
                final alert = alerts[index];
                return ListTile(
                  title: Text(alert.message),
                  subtitle: Text('Shared by: ${alert.username}'),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(hintText: 'Send an alert...'),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _controller.text.trim().isEmpty
                      ? null
                      : () => _sendAlert(_controller.text),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: _buildQuickReplies(),
          ),
        ],
      ),
    );
  }
}

class AlertMessage {
  final String username;
  final String message;

  AlertMessage({required this.username, required this.message});

  factory AlertMessage.fromJson(Map<String, dynamic> json) {
    return AlertMessage(
      username: json['username'] ?? '',
      message: json['message'] ?? '',
    );
  }
}
