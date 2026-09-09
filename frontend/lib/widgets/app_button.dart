import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

enum AppButtonType { primary, secondary }

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final AppButtonType type;
  final IconData? icon;
  final bool iconAfterText;
  final bool isLoading;
  final bool large;

  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.type = AppButtonType.primary,
    this.icon,
    this.iconAfterText = false,
    this.isLoading = false,
    this.large = false,
  });

  @override
  Widget build(BuildContext context) {
    final isPrimary = type == AppButtonType.primary;

    final buttonStyle = ButtonStyle(
      minimumSize: const WidgetStatePropertyAll(Size(double.infinity, 52)),
      padding: const WidgetStatePropertyAll(
        EdgeInsets.symmetric(horizontal: 18),
      ),
      shape: WidgetStatePropertyAll(
        RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
      backgroundColor: isPrimary
          ? WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.disabled)) {
                return AppTheme.primary.withValues(alpha: 0.35);
              }

              return AppTheme.primary;
            })
          : const WidgetStatePropertyAll(Colors.transparent),
      foregroundColor: isPrimary
          ? WidgetStateProperty.resolveWith((states) {
              return Colors.white;
            })
          : const WidgetStatePropertyAll(AppTheme.darkBlue),
      side: isPrimary
          ? null
          : const WidgetStatePropertyAll(BorderSide(color: Color(0xFFD6E2EF))),
      elevation: const WidgetStatePropertyAll(0),
    );

    final child = isLoading
        ? const SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: Colors.white,
            ),
          )
        : Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (icon != null && !iconAfterText) ...[
                Icon(icon, size: large ? 22 : 18),
                const SizedBox(width: 8),
              ],
              Text(
                label,
                style: TextStyle(
                  fontSize: large ? 16 : 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (icon != null && iconAfterText) ...[
                const SizedBox(width: 8),
                Icon(icon, size: large ? 22 : 18),
              ],
            ],
          );

    if (isPrimary) {
      return ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: buttonStyle,
        child: child,
      );
    }

    return OutlinedButton(
      onPressed: isLoading ? null : onPressed,
      style: buttonStyle,
      child: child,
    );
  }
}
