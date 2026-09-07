import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../widgets/app_logo.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBlue,
      body: Stack(
        children: [
          Positioned(
            left: -110,
            right: -110,
            bottom: 200,
            child: SizedBox(
              height: 260,
              child: Opacity(
                opacity: 0.60,
                child: Image.asset(
                  'assets/images/krakow_skyline.png',
                  fit: BoxFit.cover,
                  alignment: Alignment.bottomCenter,
                ),
              ),
            ),
          ),

          SafeArea(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 430),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final isCompact = constraints.maxHeight < 700;

                      return Column(
                        children: [
                          AppLogo(width: isCompact ? 195 : 220),
                          RichText(
                            text: TextSpan(
                              style: TextStyle(
                                fontSize: isCompact ? 34 : 38,
                                fontWeight: FontWeight.w800,
                              ),
                              children: const [
                                TextSpan(
                                  text: 'e',
                                  style: TextStyle(color: AppTheme.primary),
                                ),
                                TextSpan(
                                  text: '-Patrol',
                                  style: TextStyle(color: Colors.white),
                                ),
                              ],
                            ),
                          ),

                          SizedBox(height: isCompact ? 22 : 30),

                          const Text(
                            'Czystsze i bezpieczniejsze\nmiasto. Razem.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontSize: 20,
                              height: 1.4,
                              fontWeight: FontWeight.w600,
                              color: Colors.white,
                            ),
                          ),

                          const Spacer(),

                          FilledButton(
                            style: FilledButton.styleFrom(
                              backgroundColor: Colors.white,
                              foregroundColor: AppTheme.darkBlue,
                            ),
                            onPressed: () {
                              Navigator.pushNamed(context, '/login');
                            },
                            child: const Text('Zaloguj się'),
                          ),

                          const SizedBox(height: 14),

                          OutlinedButton(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.white,
                              side: const BorderSide(color: Colors.white),
                            ),
                            onPressed: () {
                              Navigator.pushNamed(context, '/register');
                            },
                            child: const Text('Utwórz konto'),
                          ),

                          SizedBox(height: isCompact ? 18 : 28),

                          const Text(
                            'Zgłaszaj. Zmieniaj. Twórz lepsze miasto.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      );
                    },
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
