import 'package:flutter/material.dart';
import 'package:nfz/pages/home_page.dart';
import 'package:nfz/pages/chat_page.dart';


class SelectionPage extends StatelessWidget {
  final String username;

  const SelectionPage({super.key, required this.username});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome, $username'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => HomePage(username: username),
                  ),
                );
              },
              child: const Text('View Emails'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ChatPage(username: username),
                  ),
                );
              },
              child: const Text('Open Chat'),
            ),
          ],
        ),
      ),
    );
  }
}
