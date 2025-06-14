{ inputs, lib, ... }:

let self = inputs.self;

in {
  perSystem = { system, pkgs, ... }: {
    _module.args.pkgs = lib.mkForce (import inputs.nixpkgs {
      inherit system;
      overlays = [
        (final: prev: {
          frontend =
            final.callPackage ./frontend { };
          pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
            (python-final: python-prev: {
              backend = python-final.callPackage ./backend {
                inherit (final) frontend;
              };
            })
          ];
        })
      ];
    });

    packages = {
      inherit (pkgs) frontend;
      inherit (pkgs.python3Packages) backend;
      default = pkgs.python3Packages.backend;
      
    };
    checks.run-unit-tests = pkgs.python3Packages.backend;
  };
}