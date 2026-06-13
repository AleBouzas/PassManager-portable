# Gestor de Contraseñas Portable

**Autor:** Alejandro Bouzas
**Tipo de licencia:** Freeware (gratuito)

---

## Descripción

Aplicación portable para Windows que permite almacenar y organizar
contraseñas de forma local y cifrada, sin necesidad de conexión a Internet.
Pensada para llevarse en un pendrive y usarse en cualquier PC.

---

## Aviso de responsabilidad (Disclaimer)

- Este programa se distribuye **"tal cual" (as-is)**, sin garantías de
  ningún tipo, expresas o implícitas, incluyendo (pero no limitado a)
  garantías de funcionamiento ininterrumpido, ausencia de errores o
  adecuación a un propósito particular.

- El uso de esta aplicación es de **responsabilidad exclusiva del usuario**.
  El autor no se hace responsable por pérdida de datos, contraseñas
  olvidadas, fallos del dispositivo (pendrive/PC), ni por cualquier daño
  directo o indirecto derivado del uso o mal uso del programa.

- **No existe recuperación de contraseña maestra.** Si el usuario olvida la
  contraseña maestra, los datos almacenados en `vault.db` quedan
  permanentemente inaccesibles. Esto es una característica de seguridad, no
  un defecto.

- Se recomienda **realizar copias de seguridad periódicas** del archivo
  `vault.db` en un medio adicional y confiable.

- El autor no garantiza compatibilidad con todas las versiones de Windows ni
  con todos los antivirus. Algunos antivirus pueden generar falsos positivos
  con ejecutables creados con PyInstaller; esto no implica que el programa
  contenga código malicioso (ver sección de verificación más abajo).

---

## Verificación de integridad del ejecutable

Para confirmar que el archivo `PassManager.exe` que tenés **no fue
manipulado ni alterado** respecto al original publicado por el autor,
podés calcular su huella digital (hash SHA-256).

### Pasos

1. Abrí el **Símbolo del sistema (CMD)** en la carpeta donde está el archivo.
2. Ejecutá el siguiente comando:

   ```
   certutil -hashfile PassManager.exe SHA256
   ```

3. El resultado debería ser exactamente el siguiente:

   ```
   a57d0c1f528feaa0e9c490a9ba69983fdc5431786e9ce8505047b8b8587f672d
   CertUtil: -hashfile comando completado correctamente.
   ```

Si el valor obtenido **coincide exactamente** con el de arriba, el archivo es
idéntico al original y no fue modificado. Si **no coincide**, no lo
ejecutes y descargá una copia nueva desde la fuente oficial.

> Nota: `certutil` es una herramienta incluida en Windows; no requiere
> instalar nada adicional.

---

## Sobre el programa

- Es **freeware**: gratuito, sin limitaciones de tiempo ni funciones, y sin
  ningún tipo de publicidad.

- Funciona **100% offline**: no se conecta a Internet ni envía información a
  ningún servidor.

- El cifrado utilizado se basa en estándares públicos y ampliamente
  auditados (PBKDF2-HMAC-SHA256 + AES vía Fernet). Más detalles dentro de la
  propia aplicación, en el botón **"❓ Ayuda"**.

---

## Sobre alertas de antivirus (falsos positivos conocidos)

Al subir `PassManager.exe` a [VirusTotal](https://www.virustotal.com), es
posible que algunos motores de antivirus (típicamente 5 a 10 de un total de
~70) lo marquen como sospechoso, con etiquetas genéricas como:

- "dropper"
- "Suspicious PE" / "Static AI - Suspicious"
- "Win/malicious_confidence_XX%"
- "BehavesLike.Win64.Dropper"

**Esto es un falso positivo conocido y muy común** en programas compilados
con **PyInstaller** (la herramienta usada para convertir este programa de
Python a .exe). El motivo es que PyInstaller empaqueta y descomprime código
en memoria al ejecutarse — un comportamiento que también usan algunos
malwares para ocultarse, por lo que los antivirus heurísticos marcan
*cualquier* ejecutable hecho con esta herramienta, sin que eso implique que
contenga código malicioso real.

**Cómo verificarlo vos mismo:**

- Si los motores que marcan el archivo dan nombres genéricos (como los de
  arriba) y NO hay coincidencia entre los grandes motores de referencia
  (Microsoft Defender, Kaspersky, BitDefender, Avast, ESET, etc. aparecen
  como "Undetected"), se trata de heurística genérica y no de detección de
  un virus conocido.
- Podés verificar la integridad del archivo con el hash SHA-256 (ver sección
  anterior). Si el hash coincide con el publicado, el archivo es exactamente
  el que compiló el autor a partir del código fuente disponible.
- El código fuente completo está disponible para su revisión; cualquiera con
  conocimientos de Python puede compararlo con el ejecutable.

Si aun así preferís no usar el .exe, podés ejecutar directamente el archivo
`passmanager.py` con Python instalado (requiere la librería `cryptography`),
sin pasar por ningún ejecutable compilado.

---


Si esta aplicación te resulta útil y querés apoyar al creador, podés hacer
una donación voluntaria:

- Desde la propia aplicación, con el botón **"💛 Donar"**.
- O directamente desde este enlace: http://paypal.me/AlejandroBouzas

Muchas gracias.
