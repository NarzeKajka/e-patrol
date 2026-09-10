import 'package:flutter/material.dart';

import '../../services/api_service.dart';
import '../../services/auth_storage.dart';
import '../../services/location_service.dart';
import '../../theme/app_theme.dart';
import '../../utils/report_category.dart';

class ReportDetailsScreen extends StatefulWidget {
  final int reportId;

  const ReportDetailsScreen({super.key, required this.reportId});

  @override
  State<ReportDetailsScreen> createState() => _ReportDetailsScreenState();
}

class _ReportDetailsScreenState extends State<ReportDetailsScreen> {
  bool isLoading = true;
  Map<String, dynamic>? report;
  String? address;

  @override
  void initState() {
    super.initState();
    _loadReport();
  }

  Future<void> _loadReport() async {
    try {
      final token = await AuthStorage.getToken();

      if (token == null) {
        throw Exception('Brak aktywnej sesji.');
      }

      final loadedReport = await ApiService.getReport(
        token: token,
        reportId: widget.reportId,
      );

      final latitude = double.tryParse(
        loadedReport['latitude']?.toString() ?? '',
      );

      final longitude = double.tryParse(
        loadedReport['longitude']?.toString() ?? '',
      );

      String? loadedAddress;

      if (latitude != null && longitude != null) {
        try {
          loadedAddress = await LocationService.getAddress(latitude, longitude);
        } catch (_) {
          loadedAddress = null;
        }
      }

      if (!mounted) return;

      setState(() {
        report = loadedReport;
        address = loadedAddress;
        isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Nie udało się pobrać zgłoszenia.')),
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

  String _formatCoordinates(dynamic latitude, dynamic longitude) {
    if (latitude == null || longitude == null) {
      return 'Brak lokalizacji';
    }

    final lat = double.tryParse(latitude.toString());
    final lon = double.tryParse(longitude.toString());

    if (lat == null || lon == null) {
      return 'Brak lokalizacji';
    }

    return '${lat.toStringAsFixed(6)}, ${lon.toStringAsFixed(6)}';
  }

  String _formatDate(dynamic value) {
    if (value == null) {
      return 'Brak danych';
    }

    final date = DateTime.tryParse(value.toString());

    if (date == null) {
      return 'Brak danych';
    }

    final localDate = date.toLocal();

    return '${localDate.day.toString().padLeft(2, '0')}.'
        '${localDate.month.toString().padLeft(2, '0')}.'
        '${localDate.year} '
        '${localDate.hour.toString().padLeft(2, '0')}:'
        '${localDate.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Szczegóły zgłoszenia')),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : report == null
          ? const _ErrorState()
          : _buildContent(),
    );
  }

  Widget _buildContent() {
    final currentReport = report!;

    final category = currentReport['category']?.toString() ?? '';
    final status = currentReport['status']?.toString();
    final description = currentReport['description']?.toString().trim();

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0xFFE7ECF2)),
            ),
            child: Row(
              children: [
                Container(
                  width: 54,
                  height: 54,
                  decoration: BoxDecoration(
                    color: const Color(0xFFEDF6FF),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: Icon(
                    ReportCategory.icon(category),
                    color: AppTheme.primary,
                    size: 28,
                  ),
                ),

                const SizedBox(width: 14),

                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Zgłoszenie #${currentReport['id']}',
                        style: const TextStyle(
                          fontSize: 13,
                          color: Color(0xFF718096),
                        ),
                      ),

                      const SizedBox(height: 4),

                      Text(
                        ReportCategory.label(category),
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.darkBlue,
                        ),
                      ),

                      const SizedBox(height: 8),

                      Row(
                        children: [
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              color: _statusColor(status),
                              shape: BoxShape.circle,
                            ),
                          ),

                          const SizedBox(width: 7),

                          Text(
                            _statusLabel(status),
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.w700,
                              color: _statusColor(status),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 22),

          _DetailCard(
            icon: Icons.calendar_today_outlined,
            title: 'Data zgłoszenia',
            value: _formatDate(currentReport['created_at']),
          ),

          const SizedBox(height: 8),

          _DetailCard(
            icon: Icons.location_on_outlined,
            title: 'Lokalizacja',
            value:
                address ??
                _formatCoordinates(
                  currentReport['latitude'],
                  currentReport['longitude'],
                ),
          ),

          const SizedBox(height: 8),

          _DetailCard(
            icon: Icons.notes_rounded,
            title: 'Opis',
            value: description == null || description.isEmpty
                ? 'Brak dodatkowego opisu'
                : description,
            muted: description == null || description.isEmpty,
          ),
        ],
      ),
    );
  }
}

class _DetailCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final bool muted;

  const _DetailCard({
    required this.icon,
    required this.title,
    required this.value,
    this.muted = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE0E8F1)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              color: const Color(0xFFEAF4FF),
              borderRadius: BorderRadius.circular(10),
            ),
            alignment: Alignment.center,
            child: Icon(icon, size: 20, color: AppTheme.primary),
          ),

          const SizedBox(width: 12),

          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF718096),
                  ),
                ),

                const SizedBox(height: 4),

                Text(
                  value,
                  style: TextStyle(
                    fontSize: 15,
                    height: 1.35,
                    fontWeight: FontWeight.w600,
                    color: muted ? const Color(0xFF9AA9BC) : AppTheme.darkBlue,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          'Nie udało się wyświetlić zgłoszenia.',
          textAlign: TextAlign.center,
          style: TextStyle(color: AppTheme.darkBlue, fontSize: 16),
        ),
      ),
    );
  }
}
