import 'package:flutter/material.dart';

import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/auth/welcome_screen.dart';
import 'screens/main_screen.dart';
import 'screens/reports/create/new_report_screen.dart';

import 'theme/app_theme.dart';

class EPatrolApp extends StatelessWidget {
  const EPatrolApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'e-Patrol',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,

      initialRoute: '/',

      routes: {
        '/': (context) => const WelcomeScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/home': (context) => const MainScreen(user: {}),
        '/new-report': (context) => const NewReportScreen(),
      },
    );
  }
}
