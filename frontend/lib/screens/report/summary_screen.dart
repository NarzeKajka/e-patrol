import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../theme/app_theme.dart';
import '../../widgets/report_progress.dart';
import '../../widgets/report_bottom_bar.dart';
import '../../utils/report_category.dart';

class SummaryScreen extends StatelessWidget {
  final XFile image;
  final String category;
  final double latitude;
  final double longitude;
  final String address;
  final String? description;

  const SummaryScreen({
    super.key,
    required this.image,
    required this.category,
    required this.latitude,
    required this.longitude,
    required this.address,
    this.description,
  });

  bool get hasDescription =>
      description != null && description!.trim().isNotEmpty;

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
                        File(image.path),
                        width: double.infinity,
                        height: 190,
                        fit: BoxFit.cover,
                      ),
                    ),

                    const SizedBox(height: 18),

                    _SummaryCard(
                      icon: ReportCategory.icon(category),
                      title: 'Kategoria',
                      value: ReportCategory.label(category),
                    ),

                    const SizedBox(height: 12),

                    _SummaryCard(
                      icon: Icons.location_on_outlined,
                      title: 'Lokalizacja zdarzenia',
                      value: address,
                    ),

                    const SizedBox(height: 12),

                    _SummaryCard(
                      icon: Icons.notes_rounded,
                      title: 'Opis',
                      value: hasDescription
                          ? description!.trim()
                          : 'Brak dodatkowego opisu',
                      muted: !hasDescription,
                    ),
                  ],
                ),
              ),
            ),
            ReportBottomBar(
              leftLabel: 'Wstecz',
              rightLabel: 'Wyślij',
              leftIcon: Icons.arrow_back_rounded,
              rightIcon: Icons.send_rounded,
              onLeftPressed: () {
                Navigator.pop(context);
              },
              onRightPressed: () {
                debugPrint('Wyślij zgłoszenie');
                debugPrint('category: $category');
                debugPrint('latitude: $latitude');
                debugPrint('longitude: $longitude');
                debugPrint('address: $address');
                debugPrint('description: $description');
                debugPrint('image: ${image.path}');
              },
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
