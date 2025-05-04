import numpy as np
from bokeh.layouts import column, row
from bokeh.models import Slider, Button, CheckboxGroup, ColumnDataSource
from bokeh.plotting import figure, curdoc

# Початкові значення
fs = 1000
t = np.linspace(0, 10, fs * 10)

init_amplitude = 1.0
init_frequency = 1.0
init_phase = 0.0
init_noise_mean = 0.0
init_noise_cov = 0.1
init_window = 30

# Кеш для шуму
noise_cache = {'data': None, 'mean': None, 'cov': None}

# Функції
def generate_harmonic(a, f, p):
    return a * np.sin(2 * np.pi * f * t + p)

def generate_noise(mean, cov):
    return np.random.normal(mean, np.sqrt(cov), len(t))

def harmonic_with_noise(a, f, p, mean, cov, show):
    global noise_cache
    y = generate_harmonic(a, f, p)
    if noise_cache['data'] is None or noise_cache['mean'] != mean or noise_cache['cov'] != cov:
        noise_cache['data'] = generate_noise(mean, cov)
        noise_cache['mean'] = mean
        noise_cache['cov'] = cov
    return y + noise_cache['data'] if show else y

def moving_average(signal, window_size):
    kernel = np.ones(window_size) / window_size
    return np.convolve(signal, kernel, mode='same')

# Джерела даних
source_clean = ColumnDataSource(data=dict(x=t, y=generate_harmonic(init_amplitude, init_frequency, init_phase)))
source_noisy = ColumnDataSource(data=dict(x=t, y=harmonic_with_noise(init_amplitude, init_frequency, init_phase, init_noise_mean, init_noise_cov, True)))
source_filtered = ColumnDataSource(data=dict(x=t, y=moving_average(source_noisy.data['y'], init_window)))

# Побудова графіків
plot_clean = figure(title="Чиста гармоніка", height=250, width=800)
r_clean = plot_clean.line('x', 'y', source=source_clean, color='green', legend_label='Clean')

plot_noisy = figure(title="Гармоніка з шумом", height=250, width=800)
r_noisy = plot_noisy.line('x', 'y', source=source_noisy, color='orange', legend_label='Noisy')

plot_filtered = figure(title="Фільтрована гармоніка", height=250, width=800)
r_filtered = plot_filtered.line('x', 'y', source=source_filtered, color='blue', line_dash='dashed', legend_label='Filtered')

# Віджети
slider_ampl = Slider(title="Амплітуда", start=0.1, end=5.0, value=init_amplitude, step=0.1)
slider_freq = Slider(title="Частота", start=0.1, end=5.0, value=init_frequency, step=0.1)
slider_phase = Slider(title="Фаза", start=0.0, end=2*np.pi, value=init_phase, step=0.1)
slider_mean = Slider(title="Середнє шуму", start=-1.0, end=1.0, value=init_noise_mean, step=0.05)
slider_cov = Slider(title="Дисперсія шуму", start=0.01, end=1.0, value=init_noise_cov, step=0.01)
slider_window = Slider(title="Розмір вікна фільтра", start=1, end=500, value=init_window, step=1)
checkbox = CheckboxGroup(labels=["Показати шум", "Показати фільтр"], active=[0, 1])
reset_btn = Button(label="Скинути", button_type="success")

# Оновлення
def update(attr, old, new):
    a = slider_ampl.value
    f = slider_freq.value
    p = slider_phase.value
    m = slider_mean.value
    v = slider_cov.value
    w = int(slider_window.value)
    show_n = 0 in checkbox.active
    show_f = 1 in checkbox.active

    y_clean = generate_harmonic(a, f, p)
    y_noisy = harmonic_with_noise(a, f, p, m, v, show_n)
    y_filtered = moving_average(y_noisy, w)

    source_clean.data = dict(x=t, y=y_clean)
    source_noisy.data = dict(x=t, y=y_noisy)
    source_filtered.data = dict(x=t, y=y_filtered)

    r_noisy.visible = show_n
    r_filtered.visible = show_f

# Скидання
def reset():
    slider_ampl.value = init_amplitude
    slider_freq.value = init_frequency
    slider_phase.value = init_phase
    slider_mean.value = init_noise_mean
    slider_cov.value = init_noise_cov
    slider_window.value = init_window
    checkbox.active = [0, 1]
    noise_cache['data'] = None
    update(None, None, None)

# Прив'язка подій
for wdg in [slider_ampl, slider_freq, slider_phase, slider_mean, slider_cov, slider_window]:
    wdg.on_change('value', update)
checkbox.on_change('active', update)
reset_btn.on_click(reset)

# Компоновка
controls = column(slider_ampl, slider_freq, slider_phase,
                  slider_mean, slider_cov, slider_window,
                  checkbox, reset_btn)
layout = column(plot_clean, plot_noisy, plot_filtered, controls)
curdoc().add_root(layout)
curdoc().title = "Інтерактивна гармоніка з фільтром"