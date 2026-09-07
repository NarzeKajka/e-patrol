import 'package:flutter/material.dart';

class AppLogo extends StatelessWidget {
  final double width;
  final Color? color;

  const AppLogo({super.key, this.width = 140, this.color});

  @override
  Widget build(BuildContext context) {
    final image = Image.asset(
      'assets/images/logo.png',
      width: width,
      fit: BoxFit.contain,
    );

    if (color == null) {
      return image;
    }

    return ColorFiltered(
      colorFilter: ColorFilter.mode(color!, BlendMode.srcIn),
      child: image,
    );
  }
}
