import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/widgets/report_bottom_bar.dart';

void main() {
  testWidgets('shows both navigation buttons', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          bottomNavigationBar: ReportBottomBar(
            leftLabel: 'Wstecz',
            rightLabel: 'Dalej',
            onLeftPressed: () {},
            onRightPressed: () {},
          ),
        ),
      ),
    );

    expect(find.text('Wstecz'), findsOneWidget);
    expect(find.text('Dalej'), findsOneWidget);
  });

  testWidgets('calls left callback', (tester) async {
    var leftPressed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          bottomNavigationBar: ReportBottomBar(
            leftLabel: 'Wstecz',
            rightLabel: 'Dalej',
            onLeftPressed: () {
              leftPressed = true;
            },
            onRightPressed: () {},
          ),
        ),
      ),
    );

    await tester.tap(find.text('Wstecz'));
    await tester.pump();

    expect(leftPressed, isTrue);
  });

  testWidgets('calls right callback', (tester) async {
    var rightPressed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          bottomNavigationBar: ReportBottomBar(
            leftLabel: 'Wstecz',
            rightLabel: 'Dalej',
            onLeftPressed: () {},
            onRightPressed: () {
              rightPressed = true;
            },
          ),
        ),
      ),
    );

    await tester.tap(find.text('Dalej'));
    await tester.pump();

    expect(rightPressed, isTrue);
  });

  testWidgets('disables right button when callback is null', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          bottomNavigationBar: ReportBottomBar(
            leftLabel: 'Wstecz',
            rightLabel: 'Dalej',
            onLeftPressed: () {},
            onRightPressed: null,
          ),
        ),
      ),
    );

    final buttons = tester.widgetList<ElevatedButton>(
      find.byType(ElevatedButton),
    );

    expect(buttons.length, 1);
    expect(buttons.first.onPressed, isNull);
  });

  testWidgets('shows optional navigation icons', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          bottomNavigationBar: ReportBottomBar(
            leftLabel: 'Wstecz',
            rightLabel: 'Dalej',
            leftIcon: Icons.arrow_back,
            rightIcon: Icons.arrow_forward,
            onLeftPressed: () {},
            onRightPressed: () {},
          ),
        ),
      ),
    );

    expect(find.byIcon(Icons.arrow_back), findsOneWidget);
    expect(find.byIcon(Icons.arrow_forward), findsOneWidget);
  });
}
