import 'package:flutter/material.dart';

import 'screens/auth/welcome_screen.dart';
import 'screens/main_screen.dart';
import 'services/api_service.dart';
import 'services/auth_storage.dart';

class SessionGate extends StatefulWidget {
  const SessionGate({super.key});

  @override
  State<SessionGate> createState() => _SessionGateState();
}

class _SessionGateState extends State<SessionGate> {
  Widget? screen;

  @override
  void initState() {
    super.initState();
    _checkSession();
  }

  Future<void> _checkSession() async {
    try {
      final token = await AuthStorage.getToken();

      if (token == null) {
        _showWelcome();
        return;
      }

      final user = await ApiService.getMe(token: token);

      if (!mounted) return;

      setState(() {
        screen = MainScreen(user: user);
      });
    } catch (_) {
      await AuthStorage.deleteToken();

      if (!mounted) return;

      _showWelcome();
    }
  }

  void _showWelcome() {
    if (!mounted) return;

    setState(() {
      screen = const WelcomeScreen();
    });
  }

  @override
  Widget build(BuildContext context) {
    if (screen != null) {
      return screen!;
    }

    return const Scaffold(body: Center(child: CircularProgressIndicator()));
  }
}
