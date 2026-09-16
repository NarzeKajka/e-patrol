import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/widgets/app_button.dart';

void main() {
  testWidgets('shows button label', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppButton(label: 'Dalej', onPressed: () {}),
        ),
      ),
    );

    expect(find.text('Dalej'), findsOneWidget);
  });

  testWidgets('calls onPressed when tapped', (tester) async {
    var pressed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppButton(
            label: 'Dalej',
            onPressed: () {
              pressed = true;
            },
          ),
        ),
      ),
    );

    await tester.tap(find.text('Dalej'));
    await tester.pump();

    expect(pressed, isTrue);
  });

  testWidgets('shows icon before text by default', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppButton(
            label: 'Wstecz',
            icon: Icons.arrow_back,
            onPressed: () {},
          ),
        ),
      ),
    );

    final icon = tester.getCenter(find.byIcon(Icons.arrow_back));
    final text = tester.getCenter(find.text('Wstecz'));

    expect(icon.dx, lessThan(text.dx));
  });

  testWidgets('shows icon after text when iconAfterText is true', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppButton(
            label: 'Dalej',
            icon: Icons.arrow_forward,
            iconAfterText: true,
            onPressed: () {},
          ),
        ),
      ),
    );

    final icon = tester.getCenter(find.byIcon(Icons.arrow_forward));
    final text = tester.getCenter(find.text('Dalej'));

    expect(icon.dx, greaterThan(text.dx));
  });

  testWidgets('shows loading indicator and disables button', (tester) async {
    var pressed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppButton(
            label: 'Wyślij',
            isLoading: true,
            onPressed: () {
              pressed = true;
            },
          ),
        ),
      ),
    );

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.text('Wyślij'), findsNothing);

    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    expect(pressed, isFalse);
  });

  testWidgets('uses OutlinedButton for secondary type', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: AppButton(
            label: 'Anuluj',
            type: AppButtonType.secondary,
            onPressed: () {},
          ),
        ),
      ),
    );

    expect(find.byType(OutlinedButton), findsOneWidget);
    expect(find.byType(ElevatedButton), findsNothing);
  });
}
