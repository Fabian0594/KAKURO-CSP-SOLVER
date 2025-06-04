# RESOLUTOR DE KAKURO - CSP CON BACKTRACKING CRONOLÓGICO
## Programación III - Actividad 08 - Grupo G1

### DESCRIPCIÓN DEL PROYECTO

Este proyecto implementa un resolutor completo de puzzles Kakuro utilizando técnicas avanzadas de **Constraint Satisfaction Problem (CSP)** con **Backtracking Cronológico**. El sistema es capaz de resolver tableros de dificultad "Muy difícil" según los estándares de Sudokumania.com.ar.

### MODELADO DEL PROBLEMA COMO CSP

#### Variables
- **Definición**: Cada celda vacía del tablero Kakuro representa una variable del CSP
- **Identificación**: Las variables se identifican por sus coordenadas (x, y) en el tablero
- **Cantidad**: Depende del tamaño y complejidad del tablero específico

#### Dominio
- **Rango**: Números enteros del 1 al 9 (inclusive)
- **Característica**: Dominio finito y discreto
- **Restricción básica**: Cada variable puede tomar exactamente uno de estos 9 valores

#### Restricciones

1. **Restricciones de Suma**:
   - La suma de todas las variables en un segmento debe igualar exactamente el valor objetivo
   - Formulación matemática: Σ(xi) = target, donde xi ∈ segmento

2. **Restricciones de Unicidad**:
   - No puede haber valores repetidos dentro del mismo segmento
   - Formulación: ∀i,j ∈ segmento, i ≠ j → xi ≠ xj

3. **Restricciones de Dominio**:
   - Cada variable debe tener un valor válido del dominio
   - 1 ≤ xi ≤ 9, ∀i

### TÉCNICAS DE RESOLUCIÓN IMPLEMENTADAS

#### 1. Backtracking Cronológico
- **Algoritmo**: Búsqueda sistemática con retroceso ordenado
- **Ventaja**: Garantiza encontrar solución si existe
- **Optimización**: Poda inteligente para reducir espacio de búsqueda

#### 2. Propagación de Restricciones (Constraint Propagation)
- **Forward Checking**: Verifica consistencia antes de asignar valores
- **Arc Consistency**: Mantiene consistencia entre variables relacionadas
- **Detección temprana**: Identifica inconsistencias antes de búsqueda completa

#### 3. Heurísticas de Ordenamiento
- **Most Constrained Variable**: Prioriza variables con menor dominio disponible
- **Least Constraining Value**: Selecciona valores que menos restringen otras variables
- **Degree Heuristic**: Considera variables con más restricciones primero

#### 4. Optimizaciones de Rendimiento
- **Memoización**: Cache de resultados para combinaciones de suma repetidas
- **Preprocesamiento**: Generación anticipada de combinaciones válidas
- **Poda por dominios**: Eliminación temprana de valores imposibles

### ARQUITECTURA DEL SISTEMA

#### Clase `Solver`
- **Responsabilidad**: Coordinación general del proceso de resolución
- **Componentes**:
  - Parser del formato de entrada
  - Gestión de estructuras de datos del CSP
  - Controlador del algoritmo principal

#### Clase `Run`
- **Responsabilidad**: Representación de restricciones individuales (segmentos)
- **Funcionalidades**:
  - Cálculo de dominios válidos
  - Verificación de consistencia
  - Propagación de restricciones

#### Funciones de Soporte
- `get_sums()`: Generación de combinaciones válidas
- `get_unique_sums()`: Optimización de combinaciones
- `combinations()`: Generador de permutaciones

### COMPLEJIDAD COMPUTACIONAL

#### Análisis Teórico
- **Caso peor**: O(9^n) donde n = número de variables
- **Caso promedio**: Significativamente menor debido a poda y propagación
- **Espacio**: O(n×m) donde m = tamaño máximo de dominio

#### Optimizaciones Aplicadas
- **Reducción exponencial**: Memoización reduce recálculos
- **Poda efectiva**: Propagación elimina ramas inválidas tempranamente
- **Heurísticas**: Ordenamiento inteligente mejora tiempo promedio

### FORMATO DE ENTRADA

El sistema acepta archivos de texto con el siguiente formato:

```
XX,XX,17,00,00
XX,XX,00,00,00
10,00,00,XX,XX

XX,XX,XX,15,XX
XX,XX,XX,00,00
XX,XX,XX,00,00
```

- **XX**: Celdas bloqueadas (no variables)
- **Números > 0**: Valores objetivo para segmentos
- **00**: Celdas vacías (variables del CSP)
- **Línea vacía**: Separador entre restricciones horizontales y verticales

### ARCHIVOS DEL PROYECTO

1. **main.py**: Implementación principal del resolutor
2. **ProgIIIG1-Act08-XXXXXX-Board.txt**: Tableros de prueba (dificultad "Muy difícil")
3. **ProgIIIG1-Act08-TG.md**: Documentación técnica (este archivo)

### INSTRUCCIONES DE USO

#### Ejecutar desde línea de comandos:
```bash
python main.py <archivo_tablero> [--debug]
```

#### Ejemplos:
```bash
python main.py kakuru1.txt
python main.py ProgIIIG1-Act08-001234-Board.txt --debug
```

### RESULTADOS Y VALIDACIÓN

El sistema ha sido probado exitosamente con:
- ✅ Tableros de ejemplo incluidos
- ✅ Tableros de dificultad "Muy difícil"
- ✅ Verificación de unicidad de soluciones
- ✅ Detección de tableros sin solución

### CONCLUSIONES

La implementación demuestra la efectividad de las técnicas CSP para resolver problemas combinatorios complejos como Kakuro. Las optimizaciones aplicadas permiten resolver tableros de alta dificultad en tiempo razonable, validando la eficacia del enfoque de Backtracking Cronológico con propagación de restricciones.

---
**Grupo**: G1  
**Materia**: Programación III  
**Actividad**: 08 - CSP y Backtracking  
**Año**: 2024 