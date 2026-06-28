import 'package:flutter/material.dart';

import 'config.dart';
import 'screens/chat_screen.dart';
import 'screens/login_screen.dart';
import 'services/api_service.dart';

void main() {
  runApp(const OrbesApp());
}

class OrbesApp extends StatefulWidget {
  const OrbesApp({super.key});

  @override
  State<OrbesApp> createState() => _OrbesAppState();
}

class _OrbesAppState extends State<OrbesApp> {
  final ApiService _api = ApiService();
  bool _ready = false;

  @override
  void initState() {
    super.initState();
    _api.loadToken().then((_) => setState(() => _ready = true));
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: const Color(0xFF6C5CE7),
        brightness: Brightness.dark,
      ),
      home: !_ready
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : _api.isAuthenticated
              ? ChatScreen(api: _api)
              : LoginScreen(api: _api),
    );
  }
}
