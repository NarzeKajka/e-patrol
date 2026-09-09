import 'package:flutter/material.dart';

class ReportCategory {
  static String label(String category) {
    switch (category) {
      case 'road_damage':
        return 'Uszkodzenie drogi';
      case 'waste':
        return 'Odpady';
      case 'graffiti':
        return 'Graffiti';
      default:
        return 'Nieznana kategoria';
    }
  }

  static IconData icon(String category) {
    switch (category) {
      case 'road_damage':
        return Icons.warning_amber_rounded;
      case 'waste':
        return Icons.delete_outline_rounded;
      case 'graffiti':
        return Icons.brush_outlined;
      default:
        return Icons.help_outline_rounded;
    }
  }
}
