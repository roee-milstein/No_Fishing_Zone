import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
runApp(PhishingDetectorApp());
}

class PhishingDetectorApp extends StatelessWidget {
@override
Widget build(BuildContext context) {
return MaterialApp(
title: 'No Fishing Zone',
theme: ThemeData(primarySwatch: Colors.blue),
home: HomePage(),
);
}
}

class HomePage extends StatefulWidget {
@override
_HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
TextEditingController _controller = TextEditingController();
String _result = '';
bool _loading = false;

Future<void> analyzeEmail(String text) async {
setState(() {
_loading = true;
_result = '';
});

    final url = Uri.parse('http://<YOUR_SERVER_IP>:5000/predict'); // עדכן לכתובת האמיתית של השרת שלך
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'message': text}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      setState(() {
        _result = data['result'] == 'phishing'
            ? '⚠️ הודעה חשודה: ייתכן שמדובר בפישינג!'
            : '✅ ההודעה נראית בטוחה.';
      });
    } else {
      setState(() {
        _result = 'שגיאה בהתחברות לשרת';
      });
    }

    setState(() {
      _loading = false;
    });
}

@override
Widget build(BuildContext context) {
return Scaffold(
appBar: AppBar(
title: Text('No Fishing Zone'),
),
body: Padding(
padding: EdgeInsets.all(16),
child: Column(
children: [
TextField(
controller: _controller,
maxLines: 5,
decoration: InputDecoration(
border: OutlineInputBorder(),
labelText: 'הדבק כאן את תוכן המייל',
),
),
SizedBox(height: 16),
ElevatedButton(
onPressed: _loading ? null : () => analyzeEmail(_controller.text),
child: Text('נתח מייל'),
),
SizedBox(height: 16),
if (_loading)
CircularProgressIndicator()
else
Text(
_result,
style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
),
],
),
),
);
}
}
