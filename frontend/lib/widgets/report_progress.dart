import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class ReportProgress extends StatelessWidget {
  final int currentStep;

  const ReportProgress({super.key, required this.currentStep});

  @override
  Widget build(BuildContext context) {
    const steps = ['Zdjęcie', 'Analiza', 'Szczegóły', 'Podsum.'];

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: List.generate(steps.length * 2 - 1, (index) {
        if (index.isOdd) {
          final connectorStep = (index + 1) ~/ 2;

          return Expanded(
            child: _ProgressConnector(isCompleted: connectorStep < currentStep),
          );
        }

        final stepIndex = index ~/ 2;
        final stepNumber = stepIndex + 1;

        return Expanded(
          child: _ProgressStep(
            number: stepNumber,
            label: steps[stepIndex],
            isActive: stepNumber == currentStep,
            isCompleted: stepNumber < currentStep,
          ),
        );
      }),
    );
  }
}

class _ProgressStep extends StatelessWidget {
  final int number;
  final String label;
  final bool isActive;
  final bool isCompleted;

  const _ProgressStep({
    required this.number,
    required this.label,
    required this.isActive,
    required this.isCompleted,
  });

  @override
  Widget build(BuildContext context) {
    final highlighted = isActive || isCompleted;

    return Column(
      children: [
        Container(
          width: 30,
          height: 30,
          decoration: BoxDecoration(
            color: highlighted ? AppTheme.primary : Colors.white,
            shape: BoxShape.circle,
            border: Border.all(
              color: highlighted ? AppTheme.primary : const Color(0xFFB9CDE3),
              width: 1.5,
            ),
          ),
          alignment: Alignment.center,
          child: isCompleted
              ? const Icon(Icons.check_rounded, color: Colors.white, size: 17)
              : Text(
                  number.toString(),
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: highlighted ? Colors.white : const Color(0xFF718096),
                  ),
                ),
        ),
        const SizedBox(height: 7),
        SizedBox(
          height: 15,
          child: FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(
              label,
              maxLines: 1,
              style: TextStyle(
                fontSize: 10,
                fontWeight: highlighted ? FontWeight.w700 : FontWeight.w500,
                color: highlighted ? AppTheme.primary : const Color(0xFF718096),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _ProgressConnector extends StatelessWidget {
  final bool isCompleted;

  const _ProgressConnector({required this.isCompleted});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 14),
      child: Divider(
        thickness: 1.5,
        color: isCompleted ? AppTheme.primary : const Color(0xFFD6E0EA),
      ),
    );
  }
}
