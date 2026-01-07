# Maintainer: Emmanuel Iguma-Ohenhen <emmanuelohenhen896@gmail.com.com>
pkgname=poli-cli
pkgver=1.0.0
pkgrel=1
pkgdesc="An apt-like pacman wrapper for Arch"
arch=('any')
url="https://github.com/krazi49/poli-cli"
license=('MIT')
depends=('python' 'pacman')
source=("${pkgname}-${pkgver}.tar.gz::${url}/archive/v${pkgver}.tar.gz")
sha256sums=('PASTE_ACTUAL_SHA256_HERE')

package() {
    # Install the script to /usr/bin and make it executable
    install -Dm755 "${srcdir}/poli-arch-${pkgver}/poli.py" "${pkgdir}/usr/bin/poli"
}
