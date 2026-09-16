class DetectionResult {
  final String className;
  final double confidence;
  final double x1;
  final double y1;
  final double x2;
  final double y2;

  const DetectionResult({
    required this.className,
    required this.confidence,
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
  });

  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      className: json['class_name'] as String,
      confidence: (json['confidence'] as num).toDouble(),
      x1: (json['x1'] as num).toDouble(),
      y1: (json['y1'] as num).toDouble(),
      x2: (json['x2'] as num).toDouble(),
      y2: (json['y2'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'class_name': className,
      'confidence': confidence,
      'x1': x1,
      'y1': y1,
      'x2': x2,
      'y2': y2,
    };
  }
}

class AnalysisResult {
  static const int maxDrawnBoxes = 3;

  static const double minDrawnConfidence = 0.25;

  final String modelName;
  final String? modelVersion;
  final double inferenceTimeMs;
  final List<DetectionResult> detections;
  final double? imageWidth;
  final double? imageHeight;
  final String? suggestedCategory;

  const AnalysisResult({
    required this.modelName,
    this.modelVersion,
    required this.inferenceTimeMs,
    required this.detections,
    this.imageWidth,
    this.imageHeight,
    this.suggestedCategory,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    final rawDetections = json['detections'] as List<dynamic>? ?? const [];

    return AnalysisResult(
      modelName: json['model_name'] as String,
      modelVersion: json['model_version'] as String?,
      inferenceTimeMs: (json['inference_time_ms'] as num).toDouble(),
      imageWidth: (json['image_width'] as num?)?.toDouble(),
      imageHeight: (json['image_height'] as num?)?.toDouble(),
      suggestedCategory: json['suggested_category'] as String?,
      detections: rawDetections
          .map((item) => DetectionResult.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }

  DetectionResult? get bestDetection {
    if (detections.isEmpty) return null;

    return detections.reduce(
      (current, next) => next.confidence > current.confidence ? next : current,
    );
  }

  String? get detectedCategory => suggestedCategory ?? bestDetection?.className;
  bool get hasDetection => detectedCategory != null;
  double? get confidence => bestDetection?.confidence;

  bool get canDrawBoxes =>
      imageWidth != null &&
      imageHeight != null &&
      imageWidth! > 0 &&
      imageHeight! > 0;

  List<DetectionResult> get drawnDetections {
    final best = bestDetection;

    if (best == null) return const [];

    final others =
        detections
            .where(
              (detection) =>
                  !identical(detection, best) &&
                  detection.className == best.className &&
                  detection.confidence >= minDrawnConfidence,
            )
            .toList()
          ..sort((a, b) => b.confidence.compareTo(a.confidence));

    return [best, ...others.take(maxDrawnBoxes - 1)];
  }

  Map<String, dynamic> toJson() {
    return {
      'model_name': modelName,
      'model_version': modelVersion,
      'inference_time_ms': inferenceTimeMs,
      'detections': detections.map((detection) => detection.toJson()).toList(),
    };
  }
}
