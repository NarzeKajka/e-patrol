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
  final String modelName;
  final String? modelVersion;
  final double inferenceTimeMs;
  final List<DetectionResult> detections;

  const AnalysisResult({
    required this.modelName,
    this.modelVersion,
    required this.inferenceTimeMs,
    required this.detections,
  });

  DetectionResult? get bestDetection {
    if (detections.isEmpty) return null;

    return detections.reduce(
      (current, next) => next.confidence > current.confidence ? next : current,
    );
  }

  String? get detectedCategory => bestDetection?.className;

  double? get confidence => bestDetection?.confidence;

  Map<String, dynamic> toJson() {
    return {
      'model_name': modelName,
      'model_version': modelVersion,
      'inference_time_ms': inferenceTimeMs,
      'detections': detections.map((detection) => detection.toJson()).toList(),
    };
  }
}
