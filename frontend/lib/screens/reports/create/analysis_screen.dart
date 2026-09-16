import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../../models/analysis_result.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_storage.dart';
import '../../../theme/app_theme.dart';
import '../../../utils/report_category.dart';
import '../../../widgets/detection_boxes.dart';
import '../../../widgets/report_bottom_bar.dart';
import '../../../widgets/report_progress.dart';
import 'details_screen.dart';

class AnalysisScreen extends StatefulWidget {
  final XFile image;

  const AnalysisScreen({super.key, required this.image});

  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  AnalysisResult? analysis;

  bool categoryConfirmed = true;
  String? selectedCategory;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _runAnalysis();
  }

  Future<void> _runAnalysis() async {
    setState(() {
      errorMessage = null;
    });

    try {
      final token = await AuthStorage.getToken();

      if (token == null) {
        throw Exception('Brak aktywnej sesji. Zaloguj się ponownie.');
      }

      final result = await ApiService.predictAnalysis(
        token: token,
        image: widget.image,
      );

      if (!mounted) return;

      setState(() {
        analysis = result;
        selectedCategory = result.detectedCategory;
        // Gdy model niczego nie rozpoznał, od razu pokazujemy listę wyboru.
        categoryConfirmed = result.hasDetection;
      });
    } catch (error) {
      if (!mounted) return;

      setState(() {
        errorMessage = error.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  void _changeConfirmation(bool value) {
    setState(() {
      categoryConfirmed = value;

      if (value) {
        selectedCategory = analysis?.detectedCategory;
      } else {
        selectedCategory = null;
      }
    });
  }

  void _goNext() {
    if (analysis == null || selectedCategory == null) return;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => DetailsScreen(
          image: widget.image,
          category: selectedCategory!,
          analysis: analysis!,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final currentAnalysis = analysis;

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Wynik analizy'),
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
                    const ReportProgress(currentStep: 2),

                    const SizedBox(height: 28),

                    Expanded(
                      child: SingleChildScrollView(
                        child: errorMessage != null
                            ? _AnalysisError(
                                message: errorMessage!,
                                onRetry: _runAnalysis,
                              )
                            : currentAnalysis == null
                            ? _AnalysisLoading(image: widget.image)
                            : _AnalysisResultView(
                                image: widget.image,
                                analysis: currentAnalysis,
                                categoryConfirmed: categoryConfirmed,
                                selectedCategory: selectedCategory,
                                onConfirmationChanged: _changeConfirmation,
                                onCategoryChanged: (value) {
                                  setState(() {
                                    selectedCategory = value;
                                  });
                                },
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            if (currentAnalysis != null || errorMessage != null)
              ReportBottomBar(
                leftLabel: 'Wstecz',
                rightLabel: 'Dalej',
                leftIcon: Icons.arrow_back_rounded,
                rightIcon: Icons.arrow_forward_rounded,
                onLeftPressed: () {
                  Navigator.pop(context);
                },
                onRightPressed: selectedCategory == null ? null : _goNext,
              ),
          ],
        ),
      ),
    );
  }
}

class _AnalysisLoading extends StatelessWidget {
  final XFile image;

  const _AnalysisLoading({required this.image});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            const SizedBox(
              width: 110,
              height: 110,
              child: CircularProgressIndicator(
                strokeWidth: 7,
                color: AppTheme.primary,
                backgroundColor: Color(0xFFDCEEFF),
              ),
            ),
            Container(
              width: 76,
              height: 76,
              decoration: const BoxDecoration(
                color: AppTheme.darkBlue,
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: const Text(
                'AI',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        ),

        const SizedBox(height: 28),

        const Text(
          'Trwa analiza zdjęcia...',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w800,
            color: AppTheme.darkBlue,
          ),
        ),

        const SizedBox(height: 10),

        const Text(
          'Model AI analizuje obraz i próbuje\nrozpoznać rodzaj problemu.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 14, height: 1.5, color: Color(0xFF68788D)),
        ),

        const SizedBox(height: 30),

        const _AnalysisStep(text: 'Przetwarzanie obrazu'),
        const _AnalysisStep(text: 'Wykrywanie obiektów'),
        const _AnalysisStep(text: 'Klasyfikacja kategorii'),
        const _AnalysisStep(text: 'Określanie pewności wyniku'),
      ],
    );
  }
}

class _AnalysisStep extends StatelessWidget {
  final String text;

  const _AnalysisStep({required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        children: [
          Container(
            width: 22,
            height: 22,
            decoration: const BoxDecoration(
              color: Color(0xFFE5F8EE),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check_rounded,
              size: 15,
              color: Color(0xFF16A765),
            ),
          ),

          const SizedBox(width: 12),

          Text(
            text,
            style: const TextStyle(fontSize: 14, color: AppTheme.darkBlue),
          ),
        ],
      ),
    );
  }
}

class _AnalysisResultView extends StatelessWidget {
  final XFile image;
  final AnalysisResult analysis;
  final bool categoryConfirmed;
  final String? selectedCategory;

  final ValueChanged<bool> onConfirmationChanged;
  final ValueChanged<String?> onCategoryChanged;

  const _AnalysisResultView({
    required this.image,
    required this.analysis,
    required this.categoryConfirmed,
    required this.selectedCategory,
    required this.onConfirmationChanged,
    required this.onCategoryChanged,
  });

  @override
  Widget build(BuildContext context) {
    final detectedCategory = analysis.detectedCategory;
    final confidence = analysis.confidence;

    // Ramki rysujemy tylko wtedy, gdy backend podał rozmiar zdjęcia.
    final drawnDetections = analysis.canDrawBoxes
        ? analysis.drawnDetections
        : const <DetectionResult>[];

    final boxLabel = detectedCategory == null || confidence == null
        ? null
        : '${ReportCategory.label(detectedCategory)} '
              '${(confidence * 100).round()}%';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(18),
          child: AspectRatio(
            aspectRatio: 4 / 3,
            child: Container(
              width: double.infinity,
              color: const Color(0xFFEEF2F7),
              // BoxFit.contain, a nie cover: uzytkownik ma potwierdzic lub
              // poprawic kategorie, wiec musi widziec CALE zdjecie - to samo,
              // ktore dostal model. Przyciete zdjecie moze ukryc obiekt,
              // na podstawie ktorego model zaproponowal kategorie.
              child: Stack(
                fit: StackFit.expand,
                children: [
                  Image.file(File(image.path), fit: BoxFit.contain),

                  // Warstwa z ramkami ma dokladnie ten sam rozmiar co
                  // kontener, wiec sama przelicza polozenie zdjecia w srodku.
                  if (drawnDetections.isNotEmpty)
                    DetectionBoxes(
                      detections: drawnDetections,
                      imageWidth: analysis.imageWidth!,
                      imageHeight: analysis.imageHeight!,
                      mainLabel: boxLabel,
                    ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 22),

        const Text(
          'Wykryto:',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w700,
            color: AppTheme.darkBlue,
          ),
        ),

        const SizedBox(height: 10),

        if (detectedCategory != null && confidence != null) ...[
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF7E8),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: const BoxDecoration(
                    color: Color(0xFFFFE3A8),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    ReportCategory.icon(detectedCategory),
                    color: AppTheme.darkBlue,
                  ),
                ),

                const SizedBox(width: 14),

                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ReportCategory.label(detectedCategory),
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                          color: AppTheme.darkBlue,
                        ),
                      ),

                      const SizedBox(height: 4),

                      Text(
                        'Pewność: ${(confidence * 100).round()}%',
                        style: const TextStyle(
                          fontSize: 13,
                          color: Color(0xFF68788D),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 10),

          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: LinearProgressIndicator(
              value: confidence,
              minHeight: 7,
              backgroundColor: const Color(0xFFE5EAF0),
              color: const Color(0xFF1DB66B),
            ),
          ),
        ],

        const SizedBox(height: 28),

        const Text(
          'Czy to poprawna kategoria?',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppTheme.darkBlue,
          ),
        ),

        const SizedBox(height: 10),

        RadioListTile<bool>(
          value: true,
          groupValue: categoryConfirmed,
          contentPadding: EdgeInsets.zero,
          activeColor: AppTheme.primary,
          title: const Text(
            'Tak, zgadza się',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppTheme.darkBlue,
            ),
          ),
          onChanged: (value) {
            if (value != null) {
              onConfirmationChanged(value);
            }
          },
        ),

        RadioListTile<bool>(
          value: false,
          groupValue: categoryConfirmed,
          contentPadding: EdgeInsets.zero,
          activeColor: AppTheme.primary,
          title: const Text(
            'Nie, wybierz inną',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: AppTheme.darkBlue,
            ),
          ),
          onChanged: (value) {
            if (value != null) {
              onConfirmationChanged(value);
            }
          },
        ),

        if (!categoryConfirmed) ...[
          const SizedBox(height: 8),

          DropdownButtonFormField<String>(
            initialValue: selectedCategory,
            decoration: const InputDecoration(hintText: 'Wybierz kategorię...'),
            items: const [
              DropdownMenuItem(
                value: 'road_damage',
                child: Text('Uszkodzenie drogi'),
              ),
              DropdownMenuItem(value: 'waste', child: Text('Odpady')),
              DropdownMenuItem(value: 'graffiti', child: Text('Graffiti')),
            ],
            onChanged: onCategoryChanged,
          ),
        ],
      ],
    );
  }
}

class _AnalysisError extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _AnalysisError({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 20),

        Container(
          width: 76,
          height: 76,
          decoration: const BoxDecoration(
            color: Color(0xFFFFE8E8),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: const Icon(
            Icons.cloud_off_rounded,
            size: 34,
            color: Color(0xFFD14343),
          ),
        ),

        const SizedBox(height: 24),

        const Text(
          'Nie udało się przeanalizować zdjęcia',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: AppTheme.darkBlue,
          ),
        ),

        const SizedBox(height: 10),

        Text(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 14,
            height: 1.5,
            color: Color(0xFF68788D),
          ),
        ),

        const SizedBox(height: 24),

        OutlinedButton.icon(
          onPressed: onRetry,
          icon: const Icon(Icons.refresh_rounded),
          label: const Text('Spróbuj ponownie'),
        ),

        const SizedBox(height: 14),

        const Text(
          'Możesz też wrócić i wybrać zdjęcie ponownie.',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 13, color: Color(0xFF9AA6B6)),
        ),
      ],
    );
  }
}
