import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:nfz/config.dart';

import 'chat_page.dart';
import 'login_page.dart';
import 'package:nfz/config.dart';

/// Home page of the No Fishing Zone app.
/// Displays user messages and emails, allows sending and deleting messages.
class HomePage extends StatefulWidget {
  final String username;
  const HomePage({super.key, required this.username});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<dynamic> userMessages = [];
  List<dynamic> emailMessages = [];
  final TextEditingController _controller = TextEditingController();

  String get displayUsername {
    final parts = widget.username.split('@');
    return parts.isNotEmpty ? parts[0] : widget.username;
  }

  @override
  void initState() {
    super.initState();
    _fetchAllMessages();
  }

  /// Fetch both user messages and emails.
  Future<void> _fetchAllMessages() async {
    await _fetchUserMessages();
    await _fetchEmailMessages();
  }

  /// Fetch user-predicted messages from the server.
  Future<void> _fetchUserMessages() async {
    try {
      final response = await http.get(
        Uri.parse('$serverUrl/get_messages?username=${widget.username}'),
      );
      if (response.statusCode == 200) {
        setState(() {
          userMessages = jsonDecode(response.body);
        });
      } else {
        print("[ERROR] Get user messages failed: ${response.body}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to get user messages: $e");
    }
  }

  /// Fetch emails from Gmail via the server.
  Future<void> _fetchEmailMessages() async {
    try {
      final fetchResponse = await http.post(
        Uri.parse('$serverUrl/fetch_emails'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': widget.username}),
      );

      if (fetchResponse.statusCode == 200) {
        final emailsResponse = await http.get(
          Uri.parse('$serverUrl/get_emails?username=${widget.username}'),
        );
        if (emailsResponse.statusCode == 200) {
          setState(() {
            emailMessages = jsonDecode(emailsResponse.body);
          });
          print("Fetched emails: ${emailsResponse.body}");
        } else {
          print("[ERROR] Get emails failed: ${emailsResponse.body}");
        }
      } else {
        print("[ERROR] Fetch emails failed: ${fetchResponse.body}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to fetch emails: $e");
    }
  }

  /// Send a message to the server for phishing prediction.
  Future<void> _sendMessage(String message) async {
    if (message.trim().isEmpty) return;

    try {
      final response = await http.post(
        Uri.parse('$serverUrl/predict_message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': widget.username,
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        _controller.clear();
        await _fetchUserMessages();
      } else {
        final data = jsonDecode(response.body);
        print("[ERROR] Predict message failed: ${data['message'] ?? 'Unknown error'}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to predict message: $e");
    }
  }

  /// Delete a user-predicted message.
  Future<void> _deleteMessage(String messageText) async {
    try {
      final response = await http.post(
        Uri.parse('$serverUrl/delete_message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': widget.username,
          'text': messageText,
        }),
      );

      if (response.statusCode == 200) {
        await _fetchUserMessages();
      } else {
        print("[ERROR] Delete message failed: ${response.body}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to delete message: $e");
    }
  }

  /// Delete an email from the email list.
  Future<void> _deleteEmail(String emailText) async {
    try {
      final response = await http.post(
        Uri.parse('$serverUrl/delete_email'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': widget.username,
          'text': emailText,
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          emailMessages.removeWhere((email) => email['message'] == emailText);
        });
      } else {
        print("[ERROR] Delete email failed: ${response.body}");
      }
    } catch (e) {
      print("[EXCEPTION] Failed to delete email: $e");
    }
  }

  /// Build a visual tile for a user message.
  Widget _buildUserMessageTile(dynamic message) {
    final String result = message['label'] ?? '';
    final bool isPhishing = result.toLowerCase() == 'phishing';

    return Card(
      color: isPhishing ? Colors.red.shade100 : Colors.green.shade100,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isPhishing ? Colors.red : Colors.green,
          width: 2,
        ),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ListTile(
        leading: Icon(
          isPhishing ? Icons.warning : Icons.check_circle,
          color: isPhishing ? Colors.red : Colors.green,
        ),
        title: Text(
          message['text'] ?? '',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        subtitle: Text(
          isPhishing ? 'Phishing detected' : 'Message safe',
          style: TextStyle(
            color: isPhishing ? Colors.red : Colors.green,
            fontSize: 12,
          ),
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete, color: Colors.grey),
          onPressed: () => _deleteMessage(message['text']),
        ),
      ),
    );
  }

  /// Build a visual tile for an email message.
  Widget _buildEmailMessageTile(dynamic email) {
    final String result = email['result'] ?? '';
    final bool isPhishing = result.toLowerCase() == 'phishing';

    return Card(
      color: isPhishing ? Colors.orange.shade100 : Colors.blue.shade100,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isPhishing ? Colors.orange : Colors.blue,
          width: 2,
        ),
      ),
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: ListTile(
        leading: Icon(
          isPhishing ? Icons.warning_amber : Icons.email,
          color: isPhishing ? Colors.orange : Colors.blue,
        ),
        title: Text(
          email['message'] ?? '',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.black87,
          ),
        ),
        subtitle: Text(
          isPhishing ? 'Phishing Email' : 'Safe Email',
          style: TextStyle(
            color: isPhishing ? Colors.orange : Colors.blue,
            fontSize: 12,
          ),
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete, color: Colors.grey),
          onPressed: () => _deleteEmail(email['message']),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        titleSpacing: 0,
        title: Row(
          children: [
            const SizedBox(width: 8),
            Image.asset('assets/logo.png', height: 36),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                'Welcome $displayUsername',
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _fetchAllMessages,
            tooltip: 'Refresh Messages and Emails',
          ),
        ],
      ),
      drawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Colors.blue),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Image.asset('assets/logo.png', height: 60),
                  const SizedBox(height: 8),
                  const Text(
                    'Menu',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                    ),
                  ),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.chat),
              title: const Text('Open Chat'),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ChatPage(username: widget.username),
                  ),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: () {
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const LoginPage(),
                  ),
                );
              },
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          const SizedBox(height: 16),
          Image.asset('assets/logo.png', height: 100),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      labelText: 'Enter message',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () => _sendMessage(_controller.text),
                  child: const Text('Send'),
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView(
              children: [
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text('Your Messages:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
                if (userMessages.isNotEmpty)
                  ...userMessages.map(_buildUserMessageTile).toList()
                else
                  const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Text('No messages found.', style: TextStyle(color: Colors.grey)),
                  ),
                const Padding(
                  padding: EdgeInsets.all(8.0),
                  child: Text('Emails from Gmail:', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ),
                if (emailMessages.isNotEmpty)
                  ...emailMessages.map(_buildEmailMessageTile).toList()
                else
                  const Padding(
                    padding: EdgeInsets.all(8.0),
                    child: Text('No emails found.', style: TextStyle(color: Colors.grey)),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
