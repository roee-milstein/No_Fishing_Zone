import 'package:flutter/material.dart';
import 'package:nfz/pages/login_page.dart';

/// Entry point of the No Fishing Zone application.
void main() {
  runApp(const MyApp());
}

/// Root widget of the No Fishing Zone app.
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'No Fishing Zone',
      debugShowCheckedModeBanner: false,
      home: const LoginPage(), // Set the initial screen to the login page
    );
  }
}
