import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../../theme/app_theme.dart';
import '../../../widgets/app_button.dart';
import '../../../widgets/report_bottom_bar.dart';
import '../../../widgets/report_progress.dart';
import 'analysis_screen.dart';

class NewReportScreen extends StatefulWidget {
  const NewReportScreen({super.key});

  @override
  State<NewReportScreen> createState() => _NewReportScreenState();
}

class _NewReportScreenState extends State<NewReportScreen> {
  final ImagePicker _picker = ImagePicker();

  XFile? selectedImage;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final image = await _picker.pickImage(source: source, imageQuality: 90);

      if (image == null) {
        return;
      }

      if (!mounted) {
        return;
      }

      setState(() {
        selectedImage = image;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            source == ImageSource.camera
                ? 'Aparat nie jest dostępny na tym urządzeniu.'
                : 'Nie udało się wybrać zdjęcia.',
          ),
        ),
      );
    }
  }

  void _removeImage() {
    setState(() {
      selectedImage = null;
    });
  }

  void _goNext() {
    if (selectedImage == null) {
      return;
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AnalysisScreen(image: selectedImage!),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: const Text('Nowe zgłoszenie'),
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
                    const ReportProgress(currentStep: 1),

                    const SizedBox(height: 32),

                    Expanded(
                      child: SingleChildScrollView(
                        child: selectedImage == null
                            ? _EmptyImageBox(
                                onCameraPressed: () {
                                  _pickImage(ImageSource.camera);
                                },
                                onGalleryPressed: () {
                                  _pickImage(ImageSource.gallery);
                                },
                              )
                            : _SelectedImageBox(
                                image: selectedImage!,
                                onCameraPressed: () {
                                  _pickImage(ImageSource.camera);
                                },
                                onGalleryPressed: () {
                                  _pickImage(ImageSource.gallery);
                                },
                                onRemovePressed: _removeImage,
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            ReportBottomBar(
              leftLabel: 'Anuluj',
              rightLabel: 'Dalej',
              rightIcon: Icons.arrow_forward_rounded,
              onLeftPressed: () {
                Navigator.pop(context);
              },
              onRightPressed: selectedImage == null ? null : _goNext,
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyImageBox extends StatelessWidget {
  final VoidCallback onCameraPressed;
  final VoidCallback onGalleryPressed;

  const _EmptyImageBox({
    required this.onCameraPressed,
    required this.onGalleryPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 42),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: const Color(0xFFB9CDE3), width: 1.5),
          ),
          child: const Column(
            children: [
              Icon(
                Icons.camera_alt_outlined,
                size: 58,
                color: AppTheme.darkBlue,
              ),

              SizedBox(height: 20),

              Text(
                'Dodaj zdjęcie',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w800,
                  color: AppTheme.darkBlue,
                ),
              ),

              SizedBox(height: 8),

              Text(
                'Zrób zdjęcie problemu lub\nwybierz je z galerii.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  height: 1.5,
                  color: Color(0xFF68788D),
                ),
              ),
            ],
          ),
        ),

        const SizedBox(height: 22),

        AppButton(
          label: 'Zrób zdjęcie',
          icon: Icons.camera_alt_outlined,
          large: true,
          onPressed: onCameraPressed,
        ),

        const SizedBox(height: 12),

        AppButton(
          label: 'Wybierz z galerii',
          type: AppButtonType.secondary,
          icon: Icons.photo_library_outlined,
          large: true,
          onPressed: onGalleryPressed,
        ),
      ],
    );
  }
}

class _SelectedImageBox extends StatelessWidget {
  final XFile image;
  final VoidCallback onCameraPressed;
  final VoidCallback onGalleryPressed;
  final VoidCallback onRemovePressed;

  const _SelectedImageBox({
    required this.image,
    required this.onCameraPressed,
    required this.onGalleryPressed,
    required this.onRemovePressed,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: AspectRatio(
            aspectRatio: 4 / 3,
            child: Image.file(
              File(image.path),
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),
        ),

        const SizedBox(height: 18),

        Row(
          children: [
            Expanded(
              child: AppButton(
                label: 'Zrób nowe',
                type: AppButtonType.secondary,
                icon: Icons.camera_alt_outlined,
                onPressed: onCameraPressed,
              ),
            ),

            const SizedBox(width: 10),

            Expanded(
              child: AppButton(
                label: 'Galeria',
                type: AppButtonType.secondary,
                icon: Icons.photo_library_outlined,
                onPressed: onGalleryPressed,
              ),
            ),
          ],
        ),

        const SizedBox(height: 8),

        TextButton.icon(
          onPressed: onRemovePressed,
          icon: const Icon(Icons.delete_outline_rounded),
          label: const Text('Usuń zdjęcie'),
        ),
      ],
    );
  }
}
