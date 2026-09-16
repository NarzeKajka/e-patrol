import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/analysis_result.dart';

class DetectionBoxes extends StatelessWidget {
  final List<DetectionResult> detections;

  final double imageWidth;
  final double imageHeight;

  final String? mainLabel;

  const DetectionBoxes({
    super.key,
    required this.detections,
    required this.imageWidth,
    required this.imageHeight,
    this.mainLabel,
  });

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        size: Size.infinite,
        painter: _DetectionPainter(
          detections: detections,
          imageWidth: imageWidth,
          imageHeight: imageHeight,
          mainLabel: mainLabel,
        ),
      ),
    );
  }
}

class _DetectionPainter extends CustomPainter {
  final List<DetectionResult> detections;
  final double imageWidth;
  final double imageHeight;
  final String? mainLabel;

  static const Color _mainColor = Color(0xFF16A765);
  static const Color _extraColor = Color.fromRGBO(22, 167, 101, 0.55);

  _DetectionPainter({
    required this.detections,
    required this.imageWidth,
    required this.imageHeight,
    required this.mainLabel,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (detections.isEmpty) return;
    if (imageWidth <= 0 || imageHeight <= 0) return;

    final scale = math.min(size.width / imageWidth, size.height / imageHeight);

    final shownWidth = imageWidth * scale;
    final shownHeight = imageHeight * scale;

    final offsetX = (size.width - shownWidth) / 2;
    final offsetY = (size.height - shownHeight) / 2;

    canvas.save();
    canvas.clipRect(Rect.fromLTWH(offsetX, offsetY, shownWidth, shownHeight));

    for (var index = 0; index < detections.length; index++) {
      final detection = detections[index];
      final isMain = index == 0;

      final rect = Rect.fromLTRB(
        offsetX + detection.x1 * scale,
        offsetY + detection.y1 * scale,
        offsetX + detection.x2 * scale,
        offsetY + detection.y2 * scale,
      );

      final paint = Paint()
        ..style = PaintingStyle.stroke
        ..strokeWidth = isMain ? 3 : 1.5
        ..color = isMain ? _mainColor : _extraColor;

      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(6)),
        paint,
      );

      if (isMain && mainLabel != null) {
        _paintLabel(canvas, rect, offsetY);
      }
    }

    canvas.restore();
  }

  void _paintLabel(Canvas canvas, Rect rect, double imageTop) {
    final textPainter = TextPainter(
      text: TextSpan(
        text: mainLabel,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();

    final plateWidth = textPainter.width + 12;
    final plateHeight = textPainter.height + 6;

    var plateTop = rect.top - plateHeight - 3;

    if (plateTop < imageTop) {
      plateTop = rect.top + 3;
    }

    final plate = Rect.fromLTWH(rect.left, plateTop, plateWidth, plateHeight);

    canvas.drawRRect(
      RRect.fromRectAndRadius(plate, const Radius.circular(4)),
      Paint()..color = _mainColor,
    );

    textPainter.paint(canvas, Offset(plate.left + 6, plate.top + 3));
  }

  @override
  bool shouldRepaint(_DetectionPainter oldDelegate) {
    return oldDelegate.detections != detections ||
        oldDelegate.imageWidth != imageWidth ||
        oldDelegate.imageHeight != imageHeight ||
        oldDelegate.mainLabel != mainLabel;
  }
}
