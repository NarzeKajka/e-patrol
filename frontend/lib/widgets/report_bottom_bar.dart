import 'package:flutter/material.dart';

import 'app_button.dart';

class ReportBottomBar extends StatelessWidget {
  final String leftLabel;
  final String rightLabel;
  final VoidCallback? onLeftPressed;
  final VoidCallback? onRightPressed;
  final IconData? leftIcon;
  final IconData? rightIcon;

  const ReportBottomBar({
    super.key,
    required this.leftLabel,
    required this.rightLabel,
    required this.onLeftPressed,
    required this.onRightPressed,
    this.leftIcon,
    this.rightIcon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
      decoration: const BoxDecoration(
        color: Color(0xFFF7F9FC),
        border: Border(
          top: BorderSide(
            color: Color(0xFFE5EDF5),
          ),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: AppButton(
                label: leftLabel,
                type: AppButtonType.secondary,
                icon: leftIcon,
                onPressed: onLeftPressed,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: AppButton(
                label: rightLabel,
                icon: rightIcon,
                iconAfterText: rightIcon != null,
                onPressed: onRightPressed,
              ),
            ),
          ],
        ),
      ),
    );
  }
}