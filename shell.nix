{ pkgs ? import <nixpkgs> {} }:

with pkgs;
let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix/";
    ref = "refs/tags/3.0.0";
  }) {};
in
mach-nix.mkPythonShell {
  requirements = ''
    seaborn
    matplotlib
    sklearn
    scipy
    numpy
  '';
}
