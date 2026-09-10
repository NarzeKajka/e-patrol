import 'package:flutter/material.dart';

import 'home/home_screen.dart';
import 'reports/reports_screen.dart';
import 'profile/profile_screen.dart';

class MainScreen extends StatefulWidget {
  final Map<String, dynamic> user;

  const MainScreen({super.key, required this.user});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int selectedIndex = 0;

  void _selectTab(int index) {
    setState(() {
      selectedIndex = index;
    });
  }

  Widget _buildCurrentScreen() {
    switch (selectedIndex) {
      case 1:
        return const ReportsScreen();

      case 2:
        return ProfileScreen(user: widget.user);

      case 0:
      default:
        return HomeScreen(
          user: widget.user,
          onOpenReports: () {
            _selectTab(1);
          },
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _buildCurrentScreen(),

      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex,
        onDestinationSelected: _selectTab,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Strona główna',
          ),
          NavigationDestination(
            icon: Icon(Icons.assignment_outlined),
            selectedIcon: Icon(Icons.assignment),
            label: 'Zgłoszenia',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profil',
          ),
        ],
      ),
    );
  }
}
