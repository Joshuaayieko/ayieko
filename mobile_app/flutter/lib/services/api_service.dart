import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config.dart';

/// Thin HTTP client for the Orbes backend. Stores the JWT in shared prefs.
class ApiService {
  static const _tokenKey = 'orbes_token';
  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(_tokenKey);
  }

  bool get isAuthenticated => _token != null;

  Future<void> _saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Uri _uri(String path) => Uri.parse('${AppConfig.apiBaseUrl}$path');

  /// Logs in and stores the access token. Returns the user map.
  Future<Map<String, dynamic>> login(String email, String password) async {
    final resp = await http.post(
      _uri('/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': email, 'password': password},
    );
    if (resp.statusCode != 200) {
      throw Exception('Login failed: ${resp.body}');
    }
    final data = jsonDecode(resp.body) as Map<String, dynamic>;
    await _saveToken(data['access_token'] as String);
    return data['user'] as Map<String, dynamic>;
  }

  /// Sends a chat message. Returns {reply, conversation_id, plan, tools_used}.
  Future<Map<String, dynamic>> sendMessage(String message,
      {int? conversationId}) async {
    final resp = await http.post(
      _uri('/chat'),
      headers: _headers,
      body: jsonEncode({
        'message': message,
        if (conversationId != null) 'conversation_id': conversationId,
      }),
    );
    if (resp.statusCode != 200) {
      throw Exception('Chat failed: ${resp.body}');
    }
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  Future<List<dynamic>> listMemories() async {
    final resp = await http.get(_uri('/memory'), headers: _headers);
    return jsonDecode(resp.body) as List<dynamic>;
  }
}
