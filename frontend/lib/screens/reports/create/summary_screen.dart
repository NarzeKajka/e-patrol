import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../../models/analysis_result.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_storage.dart';
import '../../../theme/app_theme.dart';
import '../../../utils/report_category.dart';
import '../../../widgets/report_bottom_bar.dart';
import '../../../widgets/report_progress.dart';

class SummaryScreen extends StatefulWidget {
  final XFile image;
  final String category;
  final AnalysisResult analysis;
  final double latitude;
  final double longitude;
  final String address;
  final String? description;

  const SummaryScreen({
    super.key,
    required this.image,
    required this.category,
    required this.analysis,
    required this.latitude,
    required this.longitude,
    required this.address,
    this.description,
  });

  @override
  State<SummaryScreen> createState() => _SummaryScreenState();
}

class _SummaryScreenState extends State<SummaryScreen> {
  bool isSending = false;

  bool get hasDescription =>
      widget.description != null && widget.description!.trim().isNotEmpty;

  Future<void> _submitReport() async {
    if (isSending) return;

    setState(() {
      isSending = true;
    });

    try {
      final token = await AuthStorage.getToken();

      if (token == null) {
        throw Exception('Brak aktywnej sesji. Zaloguj się ponownie.');
      }

      // 1. Tworzymy zgłoszenie.
      final report = await ApiService.createReport(
        token: token,
        category: widget.category,
        description: hasDescription ? widget.description!.trim() : null,
        latitude: widget.latitude,
        longitude: widget.longitude,
      );

      final reportId = report['id'] as int;

      // 2. Dodajemy zdjęcie do utworzonego zgłoszenia.
      final uploadedImage = await ApiService.uploadReportImage(
        token: token,
        reportId: reportId,
        image: widget.image,
      );

      final imageId = uploadedImage['id'] as int;

      // 3. Zapisujemy wynik analizy AI dla zdjęcia.
      await ApiService.createAnalysis(
        token: token,
        imageId: imageId,
        analysis: widget.analysis,
      );

      if (!mounted) return;

      await _showSuccessDialog();

      if (!mounted) return;

      final navigator = Navigator.of(context);

      navigator.popUntil((route) => route.settings.name == '/new-report');

      navigator.pop();
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(_errorMessage(e))));
    } finally {
      if (mounted) {
        setState(() {
          isSending = false;
        });
      }
    }
  }

  String _errorMessage(Object error) {
    final message = error.toString();

    if (message.startsWith('Exception: ')) {
      return message.substring('Exception: '.length);
    }

    return 'Nie udało się wysłać zgłoszenia.';
  }

  Future<void> _showSuccessDialog() {
    return showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) {
        return AlertDialog(
          icon: const Icon(
            Icons.check_circle_rounded,
            color: Color(0xFF16A765),
            size: 52,
          ),
          title: const Text('Zgłoszenie wysłane', textAlign: TextAlign.center),
          content: const Text(
            'Twoje zgłoszenie zostało przyjęte i oczekuje na obsługę.',
            textAlign: TextAlign.center,
          ),
          actionsAlignment: MainAxisAlignment.center,
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(dialogContext);
              },
              child: const Text('Gotowe'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Podsumowanie'),
      ),
      body: SafeArea(
        top: false,
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const ReportProgress(currentStep: 4),

                    const SizedBox(height: 26),

                    const Text(
                      'Sprawdź zgłoszenie',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: AppTheme.darkBlue,
                      ),
                    ),

                    const SizedBox(height: 6),

                    const Text(
                      'Upewnij się, że wszystkie informacje są poprawne przed wysłaniem.',
                      style: TextStyle(
                        fontSize: 14,
                        height: 1.4,
                        color: Color(0xFF718096),
                      ),
                    ),

                    const SizedBox(height: 24),

                    ClipRRect(
                      borderRadius: BorderRadius.circular(14),
                      child: Image.file(
                        File(widget.image.path),
                        width: double.infinity,
                        height: 190,
                        fit: BoxFit.cover,
                      ),
                    ),

                    const SizedBox(height: 18),

                    _SummaryCard(
                      icon: ReportCategory.icon(widget.category),
                      title: 'Kategoria',
                      value: ReportCategory.label(widget.category),
                    ),

                    const SizedBox(height: 12),

                    _SummaryCard(
                      icon: Icons.location_on_outlined,
                      title: 'Lokalizacja zdarzenia',
                      value: widget.address,
                    ),

                    const SizedBox(height: 12),

                    _SummaryCard(
                      icon: Icons.notes_rounded,
                      title: 'Opis',
                      value: hasDescription
                          ? widget.description!.trim()
                          : 'Brak dodatkowego opisu',
                      muted: !hasDescription,
                    ),
                  ],
                ),
              ),
            ),

            ReportBottomBar(
              leftLabel: 'Wstecz',
              rightLabel: isSending ? 'Wysyłanie...' : 'Wyślij',
              leftIcon: Icons.arrow_back_rounded,
              rightIcon: isSending ? null : Icons.send_rounded,
              onLeftPressed: isSending
                  ? null
                  : () {
                      Navigator.pop(context);
                    },
              onRightPressed: isSending ? null : _submitReport,
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final bool muted;

  const _SummaryCard({
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
