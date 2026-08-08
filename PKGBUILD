# Maintainer: Emmanuel Iguma-Ohenhen <emmanuelohenhen896@gmail.com>
pkgname=poli-cli
pkgver=3.0.0
pkgrel=1
pkgdesc="An apt-like pacman wrapper for Arch with AUR support"
arch=('any')
url="https://github.com/krazi49/poli-cli"
license=('MIT')
depends=('python' 'pacman' 'git')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('PASTE_ACTUAL_SHA256_HERE')

package() {
    # Install the poli package to /usr/lib/python3.x/site-packages
    install -d "${pkgdir}/usr/local/lib"
    cp -r "${srcdir}/${pkgname}-${pkgver}/poli" "${pkgdir}/usr/local/lib/poli"

    # Create the executable shim
    install -d "${pkgdir}/usr/local/bin"
    cat > "${pkgdir}/usr/local/bin/poli" << 'EOF'
#!/usr/bin/env bash
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}/usr/local/lib"
exec python3 -m poli "$@"
EOF
    chmod +x "${pkgdir}/usr/local/bin/poli"
}
