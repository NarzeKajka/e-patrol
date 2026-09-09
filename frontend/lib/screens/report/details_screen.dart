import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../services/location_service.dart';
import '../../theme/app_theme.dart';
import '../../utils/report_category.dart';
import '../../widgets/app_button.dart';
import '../../widgets/report_bottom_bar.dart';
import '../../widgets/report_progress.dart';
import 'location_picker_screen.dart';
import 'summary_screen.dart';

class DetailsScreen extends StatefulWidget {
  final XFile image;
  final String category;

  const DetailsScreen({super.key, required this.image, required this.category});

  @override
  State<DetailsScreen> createState() => _DetailsScreenState();
}

class _DetailsScreenState extends State<DetailsScreen> {
  final TextEditingController _descriptionController = TextEditingController();

  double? latitude;
  double? longitude;
  String? locationLabel;

  bool get hasLocation => latitude != null && longitude != null;

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _useCurrentLocation() async {
    try {
      final result = await LocationService.getCurrentLocation();

      if (!mounted) return;

      setState(() {
        latitude = result.latitude;
        longitude = result.longitude;
        locationLabel = result.address;
      });
    } catch (e) {
      if (!mounted) return;

      final message = e.toString().replaceFirst('Exception: ', '');

      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  Future<void> _chooseOnMap() async {
    final result = await Navigator.push<Map<String, dynamic>>(
      context,
      MaterialPageRoute(
        builder: (_) => LocationPickerScreen(
          initialLatitude: latitude,
          initialLongitude: longitude,
        ),
      ),
    );

    if (!mounted || result == null) return;

    setState(() {
      latitude = result['latitude'] as double?;
      longitude = result['longitude'] as double?;
      locationLabel = result['address'] as String? ?? 'Wybrana lokalizacja';
    });
  }

  void _goNext() {
    if (!hasLocation) return;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => SummaryScreen(
          image: widget.image,
          category: widget.category,
          latitude: latitude!,
          longitude: longitude!,
          address: locationLabel ?? 'Wybrana lokalizacja',
          description: _descriptionController.text.trim(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Szczegóły zgłoszenia'),
      ),
      body: SafeArea(
        top: false,
        child: Column(
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 0),
                child: Column(
                  children: [
                    const ReportProgress(currentStep: 3),

                    const SizedBox(height: 28),

                    Expanded(
                      child: SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // ZDJĘCIE + KATEGORIA
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(14),
                                  child: SizedBox(
                                    width: 80,
                                    height: 80,
                                    child: Image.file(
                                      File(widget.image.path),
                                      fit: BoxFit.cover,
                                    ),
                                  ),
                                ),

                                const SizedBox(width: 12),

                                Expanded(
                                  child: Container(
                                    height: 58,
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 14,
                                    ),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFEDF6FF),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Row(
                                      children: [
                                        Container(
                                          width: 34,
                                          height: 34,
                                          decoration: const BoxDecoration(
                                            color: Color(0xFFDCEEFF),
                                            shape: BoxShape.circle,
                                          ),
                                          child: Icon(
                                            ReportCategory.icon(
                                              widget.category,
                                            ),
                                            size: 18,
                                            color: AppTheme.primary,
                                          ),
                                        ),

                                        const SizedBox(width: 10),

                                        Expanded(
                                          child: Text(
                                            ReportCategory.label(
                                              widget.category,
                                            ),
                                            style: const TextStyle(
                                              fontSize: 14,
                                              fontWeight: FontWeight.w700,
                                              color: AppTheme.darkBlue,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),

                            const SizedBox(height: 30),

                            // LOKALIZACJA
                            const Text(
                              'Lokalizacja zdarzenia',
                              style: TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.w800,
                                color: AppTheme.darkBlue,
                              ),
                            ),

                            const SizedBox(height: 6),

                            const Text(
                              'Wskaż miejsce, w którym występuje zgłaszany problem.',
                              style: TextStyle(
                                fontSize: 14,
                                height: 1.4,
                                color: Color(0xFF68788D),
                              ),
                            ),

                            const SizedBox(height: 16),

                            AppButton(
                              label: 'Użyj bieżącej lokalizacji',
                              icon: Icons.my_location_rounded,
                              large: true,
                              onPressed: _useCurrentLocation,
                            ),

                            const SizedBox(height: 10),

                            AppButton(
                              label: 'Wybierz na mapie',
                              type: AppButtonType.secondary,
                              icon: Icons.map_outlined,
                              large: true,
                              onPressed: _chooseOnMap,
                            ),

                            if (hasLocation) ...[
                              const SizedBox(height: 16),

                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFECF9F2),
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Icon(
                                      Icons.location_on_outlined,
                                      color: Color(0xFF169B62),
                                    ),

                                    const SizedBox(width: 10),

                                    Expanded(
                                      child: Text(
                                        locationLabel ?? 'Wybrana lokalizacja',
                                        style: const TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w700,
                                          color: AppTheme.darkBlue,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],

                            const SizedBox(height: 30),

                            // OPIS
                            const Text(
                              'Opis',
                              style: TextStyle(
                                fontSize: 17,
                                fontWeight: FontWeight.w800,
                                color: AppTheme.darkBlue,
                              ),
                            ),

                            const SizedBox(height: 4),

                            const Text(
                              'Opcjonalnie',
                              style: TextStyle(
                                fontSize: 13,
                                color: Color(0xFF8492A6),
                              ),
                            ),

                            const SizedBox(height: 12),

                            TextField(
                              controller: _descriptionController,
                              maxLength: 500,
                              maxLines: 5,
                              minLines: 4,
                              decoration: const InputDecoration(
                                hintText:
                                    'Dodaj dodatkowe informacje o problemie...',
                                hintStyle: TextStyle(color: Color(0xFFA0AEC0)),
                              ),
                            ),

                            const SizedBox(height: 20),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            ReportBottomBar(
              leftLabel: 'Wstecz',
              rightLabel: 'Dalej',
              leftIcon: Icons.arrow_back_rounded,
              rightIcon: Icons.arrow_forward_rounded,
              onLeftPressed: () {
                Navigator.pop(context);
              },
              onRightPressed: hasLocation ? _goNext : null,
            ),
          ],
        ),
      ),
    );
  }
}
