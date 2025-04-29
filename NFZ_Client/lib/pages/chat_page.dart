import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:nfz/config.dart';

/// Chat page for users to send and view community chat messages.
class ChatPage extends StatefulWidget {
  final String username;
  const ChatPage({super.key, required this.username});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  List<dynamic> chatMessages = [];
  final TextEditingController _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchChatMessages();
  }

  /// Fetch chat messages from the server.
  Future<void> _fetchChatMessages() async {
    try {
      final response = await http.get(Uri.parse('$serverUrl/chat_messages'));
      if (response.statusCode == 200) {
        setState(() {
          chatMessages = jsonDecode(response.body);
        });
      } else {
        print("[ERROR] Failed to get chat messages: ${response.body}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to get chat messages: $e");
    }
  }

  /// Send a new chat message to the server.
  Future<void> _sendChatMessage(String message) async {
    if (message.trim().isEmpty) return;

    try {
      final response = await http.post(
        Uri.parse('$serverUrl/send_chat_message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': widget.username,
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        _controller.clear();
        await _fetchChatMessages();
      } else {
        print("[ERROR] Failed to send chat message: ${response.body}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to send chat message: $e");
    }
  }

  /// Build a visual card for each chat message.
  Widget _buildChatTile(dynamic chat) {
    final String username = chat['username'] ?? 'Anonymous';
    final String message = chat['message'] ?? '';
    final String timestamp = (chat['timestamp'] ?? '').toString();

    return Card(
      color: Colors.blue.shade50,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(
          color: Colors.blueAccent,
          width: 2,
        ),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ListTile(
        leading: const Icon(Icons.person, color: Colors.blue),
        title: Text(
          username,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message,
              style: const TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 4),
            Text(
              timestamp,
              style: const TextStyle(color: Colors.grey, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Image.asset('assets/logo.png', height: 36),
            const SizedBox(width: 8),
            const Text('Community Chat'),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: chatMessages.isEmpty
                ? const Center(
              child: Text(
                'No messages yet',
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.grey,
                ),
              ),
            )
                : ListView.builder(
              itemCount: chatMessages.length,
              itemBuilder: (context, index) => _buildChatTile(chatMessages[index]),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      labelText: 'Enter your message',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _sendChatMessage(_controller.text),
                  child: const Text('Send'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
