import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/widgets/report_progress.dart';

void main() {
  testWidgets('shows all report steps', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ReportProgress(currentStep: 1))),
    );

    expect(find.text('Zdjęcie'), findsOneWidget);
    expect(find.text('Analiza'), findsOneWidget);
    expect(find.text('Szczegóły'), findsOneWidget);
    expect(find.text('Podsum.'), findsOneWidget);
  });

  testWidgets('first step is active initially', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ReportProgress(currentStep: 1))),
    );

    expect(find.text('1'), findsOneWidget);
    expect(find.text('2'), findsOneWidget);
    expect(find.text('3'), findsOneWidget);
    expect(find.text('4'), findsOneWidget);

    expect(find.byIcon(Icons.check_rounded), findsNothing);
  });

  testWidgets('completed steps show check icons', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ReportProgress(currentStep: 3))),
    );

    expect(find.byIcon(Icons.check_rounded), findsNWidgets(2));

    expect(find.text('1'), findsNothing);
    expect(find.text('2'), findsNothing);

    expect(find.text('3'), findsOneWidget);
    expect(find.text('4'), findsOneWidget);
  });

  testWidgets('all previous steps are completed on final step', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ReportProgress(currentStep: 4))),
    );

    expect(find.byIcon(Icons.check_rounded), findsNWidgets(3));
    expect(find.text('4'), findsOneWidget);
  });
}
