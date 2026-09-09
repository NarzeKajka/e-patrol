import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/auth_storage.dart';
import '../theme/app_theme.dart';
import '../widgets/app_logo.dart';

class HomeScreen extends StatefulWidget {
  final Map<String, dynamic> user;

  const HomeScreen({super.key, required this.user});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool isLoading = true;
  List<dynamic> reports = [];

  String get firstName {
    final fullName = widget.user['full_name']?.toString().trim() ?? '';

    if (fullName.isEmpty) {
      return '';
    }

    return fullName.split(RegExp(r'\s+')).first;
  }

  int get totalReports {
    return reports.length;
  }

  int get inProgressReports {
    return reports.where((report) => report['status'] == 'in_progress').length;
  }

  int get resolvedReports {
    return reports.where((report) => report['status'] == 'resolved').length;
  }

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    try {
      final token = await AuthStorage.getToken();

      if (token == null) {
        if (!mounted) {
          return;
        }

        setState(() {
          isLoading = false;
        });

        return;
      }

      final loadedReports = await ApiService.getMyReports(token: token);

      if (!mounted) {
        return;
      }

      setState(() {
        reports = loadedReports;
        isLoading = false;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nie udało się pobrać zgłoszeń.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),

      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 110),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // HEADER
              Row(
                children: [
                  const AppLogo(width: 48, color: AppTheme.darkBlue),
                  const SizedBox(width: 10),
                  const Text.rich(
                    TextSpan(
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                      ),
                      children: [
                        TextSpan(
                          text: 'e',
                          style: TextStyle(color: AppTheme.primary),
                        ),
                        TextSpan(
                          text: '-Patrol',
                          style: TextStyle(color: AppTheme.darkBlue),
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(
                      Icons.notifications_none_rounded,
                      size: 28,
                      color: AppTheme.darkBlue,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // POWITANIE
              Text(
                firstName.isEmpty ? 'Cześć!' : 'Cześć, $firstName!',
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppTheme.darkBlue,
                ),
              ),

              Text(
                'Dziękujemy, że dbasz o nasze miasto 💙',
                style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
              ),

              const SizedBox(height: 28),

              // NOWE ZGŁOSZENIE
              InkWell(
                borderRadius: BorderRadius.circular(20),
                onTap: () async {
                  await Navigator.pushNamed(context, '/new-report');

                  if (!mounted) return;

                  _loadReports();
                },
                child: Ink(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 28,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE8F3FF),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Column(
                    children: [
                      _NewReportIcon(),
                      SizedBox(height: 16),
                      Text(
                        'Nowe zgłoszenie',
                        style: TextStyle(
                          fontSize: 21,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.darkBlue,
                        ),
                      ),
                      SizedBox(height: 6),
                      Text(
                        'Zrób zdjęcie lub wybierz z galerii',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          fontSize: 14,
                          color: Color(0xFF52637A),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 22),

              // STATYSTYKI
              Row(
                children: [
                  Expanded(
                    child: _StatisticCard(
                      icon: Icons.assignment_outlined,
                      value: isLoading ? '…' : totalReports.toString(),
                      label: 'Moje\nzgłoszenia',
                      backgroundColor: const Color(0xFFEDF6FF),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _StatisticCard(
                      icon: Icons.hourglass_top_rounded,
                      value: isLoading ? '…' : inProgressReports.toString(),
                      label: 'W\nrealizacji',
                      backgroundColor: const Color(0xFFFFF7E8),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _StatisticCard(
                      icon: Icons.verified_outlined,
                      value: isLoading ? '…' : resolvedReports.toString(),
                      label: 'Rozwiązane',
                      backgroundColor: const Color(0xFFECF9F2),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 30),

              // OSTATNIE ZGŁOSZENIA
              Row(
                children: [
                  const Text(
                    'Ostatnie zgłoszenia',
                    style: TextStyle(
                      fontSize: 19,
                      fontWeight: FontWeight.w800,
                      color: AppTheme.darkBlue,
                    ),
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () {},
                    child: const Text(
                      'Zobacz wszystkie',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // LISTA ZGŁOSZEŃ
              if (isLoading)
                const _ReportsLoading()
              else if (reports.isEmpty)
                const _EmptyReports()
              else
                Column(
                  children: reports
                      .take(3)
                      .map((report) => _RecentReportCard(report: report))
                      .toList(),
                ),
            ],
          ),
        ),
      ),

      // DOLNA NAWIGACJA
      bottomNavigationBar: NavigationBar(
        selectedIndex: 0,
        onDestinationSelected: (index) {},
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

class _NewReportIcon extends StatelessWidget {
  const _NewReportIcon();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 70,
      height: 70,
      decoration: const BoxDecoration(
        color: AppTheme.primary,
        shape: BoxShape.circle,
      ),
      child: const Icon(
        Icons.camera_alt_outlined,
        size: 34,
        color: Colors.white,
      ),
    );
  }
}

class _StatisticCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color backgroundColor;

  const _StatisticCard({
    required this.icon,
    required this.value,
    required this.label,
    required this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 132,
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 14),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 27, color: AppTheme.primary),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: AppTheme.darkBlue,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 12,
              height: 1.2,
              fontWeight: FontWeight.w500,
              color: AppTheme.darkBlue,
            ),
          ),
        ],
      ),
    );
  }
}

class _ReportsLoading extends StatelessWidget {
  const _ReportsLoading();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 30),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE7ECF2)),
      ),
      child: const Center(
        child: SizedBox(
          width: 24,
          height: 24,
          child: CircularProgressIndicator(strokeWidth: 2.5),
        ),
      ),
    );
  }
}

class _EmptyReports extends StatelessWidget {
  const _EmptyReports();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 30),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE7ECF2)),
      ),
      child: Column(
        children: [
          Icon(Icons.inbox_outlined, size: 38, color: Colors.grey.shade400),
          const SizedBox(height: 12),
          const Text(
            'Brak zgłoszeń',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              color: AppTheme.darkBlue,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Twoje ostatnie zgłoszenia pojawią się tutaj.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }
}

class _RecentReportCard extends StatelessWidget {
  final dynamic report;

  const _RecentReportCard({required this.report});

  String get categoryLabel {
    switch (report['category']) {
      case 'road_damage':
        return 'Uszkodzenie drogi';

      case 'waste':
        return 'Odpady';

      case 'graffiti':
        return 'Graffiti';

      default:
        return 'Zgłoszenie';
    }
  }

  IconData get categoryIcon {
    switch (report['category']) {
      case 'road_damage':
        return Icons.warning_amber_rounded;

      case 'waste':
        return Icons.delete_outline_rounded;

      case 'graffiti':
        return Icons.brush_outlined;

      default:
        return Icons.assignment_outlined;
    }
  }

  String get statusLabel {
    switch (report['status']) {
      case 'in_progress':
        return 'W realizacji';

      case 'resolved':
        return 'Rozwiązane';

      case 'submitted':
      default:
        return 'Zgłoszone';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE7ECF2)),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: const Color(0xFFEDF6FF),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Icon(categoryIcon, color: AppTheme.primary, size: 25),
          ),

          const SizedBox(width: 14),

          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  categoryLabel,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkBlue,
                  ),
                ),

                const SizedBox(height: 5),

                Text(
                  statusLabel,
                  style: TextStyle(fontSize: 13, color: Colors.grey.shade600),
                ),
              ],
            ),
          ),

          Icon(Icons.chevron_right_rounded, color: Colors.grey.shade400),
        ],
      ),
    );
  }
}
