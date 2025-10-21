# shell.nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    gcc
    libGL
    xorg.libX11
    xorg.libXcursor
    xorg.libXi
    xorg.libXrandr
    xorg.libXinerama
    xorg.libXxf86vm
    libpng
    libjpeg
    freetype
  ];

  LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    pkgs.stdenv.cc.cc.lib      # ✅ Toujours disponible
    pkgs.gcc-unwrapped.lib
    pkgs.libGL
    pkgs.xorg.libX11
    pkgs.xorg.libXcursor
    pkgs.xorg.libXi
    pkgs.xorg.libXrandr
    pkgs.xorg.libXinerama
    pkgs.xorg.libXxf86vm
  ];

  shellHook = ''
    echo "✅ Environnement système prêt pour Ursina."
    echo "➡️  Active ton venv : source venv/bin/activate"
  '';
}
