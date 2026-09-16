import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/utils/report_category.dart';

void main() {
  group('ReportCategory', () {
    test('returns correct labels', () {
      expect(ReportCategory.label('road_damage'), 'Uszkodzenie drogi');

      expect(ReportCategory.label('waste'), 'Odpady');

      expect(ReportCategory.label('graffiti'), 'Graffiti');
    });

    test('returns fallback label for unknown category', () {
      expect(ReportCategory.label('something_else'), 'Nieznana kategoria');
    });

    test('returns correct icons', () {
      expect(ReportCategory.icon('road_damage'), Icons.warning_amber_rounded);

      expect(ReportCategory.icon('waste'), Icons.delete_outline_rounded);

      expect(ReportCategory.icon('graffiti'), Icons.brush_outlined);
    });

    test('returns fallback icon for unknown category', () {
      expect(ReportCategory.icon('something_else'), Icons.help_outline_rounded);
    });
  });
}
