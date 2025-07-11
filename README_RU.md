# GenPlan : Generation Vector Residential Plans Based on the Textual Description

Контакты: [Егор Баженов](mailto:tujh.bazhenov.kbn00@mail.ru)

## Схема метода

![](examples/scheme.png) 

Мы представляем наш новый алгоритм генерации векторных планов жилых
помещений на основе текстового описания.

## Пример генерации
| Текстовое описание                                                                                                                                                                                                                     | Растровое изображение        | Векторное изображение        |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|------------------------------|
| A minimalist 2D floor plan of an empty studio apartment without any text, featuring clean black lines and white spaces, showcasing an open layout with designated areas for living, sleeping, and kitchen.  without words on a picture | ![](examples/pngs/test3.png) | ![](examples/svgs/test3.svg) |

## Использование

1. ``git clone https://github.com/CTLab-ITMO/GenPlan``
2. ``pip install requirements.txt``
3. ``python pipline.py --text "your text promt" --output_svg "svg_path" --generation_model "model_name"``

## Настройка параметров

Настройки для вашей задачи можно выполнять с помощью [файла конфигурации](config.py). 

| Имя параметра      | Описание                                                                | Тип     |
|--------------------|-------------------------------------------------------------------------|---------|
| PNG_PATH           | Путь к сегенерированному растровому изображению                         | String  |
| CLEAN_PNG_PATH     | Путь к обработанному растровому изображению                             | String  |
| BLACK_COLOR_BORDER | Максимальное значение цветовой фильтрации                               | Float   |
| MAX_PERCENTILE     | Максимальная разница пикселей в процентах                               | Float   |
| MAX_VALUE          | Максимальное количество непохожих пикселей                              | Integer |
| MIN_THICKNESS      | Минимальная толщина векторной линии                                     | Integer |
| MAX_DEVIATION      | Максимальное отклонение точек от прямой линии                           | Integer |
| LOSS_SCALE         | Значение скалирования для white loss                                    | Float   |
| EDGING_TYPE        | Тип маски                                                               | String  |
| USE_WHITE_LOSS     | Используется ли white loss (реализовано только с генератором типа SDXL) | Boolean |

