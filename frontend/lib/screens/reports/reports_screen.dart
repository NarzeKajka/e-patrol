import 'package:flutter/material.dart';

import '../../services/api_service.dart';
import '../../services/auth_storage.dart';
import '../../theme/app_theme.dart';
import '../../utils/report_category.dart';
import 'report_details_screen.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  bool isLoading = true;
  List<dynamic> reports = [];

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    try {
      final token = await AuthStorage.getToken();

      if (token == null) {
        throw Exception('Brak aktywnej sesji.');
      }

      final loadedReports = await ApiService.getMyReports(token: token);

      if (!mounted) return;

      setState(() {
        reports = loadedReports;
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nie udało się pobrać zgłoszeń.')),
      );
    }
  }

  String _statusLabel(String? status) {
    switch (status) {
      case 'in_progress':
        return 'W realizacji';
      case 'resolved':
        return 'Rozwiązane';
      case 'submitted':
      default:
        return 'Zgłoszone';
    }
  }

  Color _statusColor(String? status) {
    switch (status) {
      case 'in_progress':
        return const Color(0xFFD99000);
      case 'resolved':
        return const Color(0xFF16A765);
      case 'submitted':
      default:
        return AppTheme.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Moje zgłoszenia'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadReports,
        child: isLoading
            ? const Center(child: CircularProgressIndicator())
            : reports.isEmpty
            ? const _EmptyReports()
            : ListView.separated(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
                itemCount: reports.length,
                separatorBuilder: (_, _) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final report = reports[index];

                  return _ReportCard(
                    report: report,
                    statusLabel: _statusLabel(report['status']?.toString()),
                    statusColor: _statusColor(report['status']?.toString()),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => ReportDetailsScreen(
                            reportId: report['id'] as int,
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
      ),
    );
  }
}

class _ReportCard extends StatelessWidget {
  final dynamic report;
  final String statusLabel;
  final Color statusColor;
  final VoidCallback onTap;

  const _ReportCard({
    required this.report,
    required this.statusLabel,
    required this.statusColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final category = report['category']?.toString() ?? '';

    return InkWell(
      borderRadius: BorderRadius.circular(18),
      onTap: onTap,
      child: Ink(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: const Color(0xFFE7ECF2)),
        ),
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: const Color(0xFFEDF6FF),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                ReportCategory.icon(category),
                color: AppTheme.primary,
                size: 26,
              ),
            ),

            const SizedBox(width: 14),

            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    ReportCategory.label(category),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.darkBlue,
                    ),
                  ),

                  const SizedBox(height: 7),

                  Row(
                    children: [
                      Container(
                        width: 7,
                        height: 7,
                        decoration: BoxDecoration(
                          color: statusColor,
                          shape: BoxShape.circle,
                        ),
                      ),

                      const SizedBox(width: 7),

                      Text(
                        statusLabel,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: statusColor,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            Icon(Icons.chevron_right_rounded, color: Colors.grey.shade400),
          ],
        ),
      ),
    );
  }
}

class _EmptyReports extends StatelessWidget {
  const _EmptyReports();

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const SizedBox(height: 100),

        Icon(Icons.assignment_outlined, size: 54, color: Colors.grey.shade400),

        const SizedBox(height: 16),

        const Text(
          'Brak zgłoszeń',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 19,
            fontWeight: FontWeight.w700,
            color: AppTheme.darkBlue,
          ),
        ),

        const SizedBox(height: 8),

        Text(
          'Twoje zgłoszenia pojawią się tutaj.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 14, color: Colors.grey.shade600),
        ),
      ],
    );
  }
}
