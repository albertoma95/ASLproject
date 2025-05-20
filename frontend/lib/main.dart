import 'package:flutter/material.dart';
import 'camera_web_preview.dart'; // Importa el nuevo archivo

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cámara Web',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: WebCameraPage(), // Aquí usas el widget de la cámara
    );
  }
}
