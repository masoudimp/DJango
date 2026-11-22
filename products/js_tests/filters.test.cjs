const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');

function setup() {
    function element(value = '') {
        const listeners = {};
        return {
            value, textContent: '', innerHTML: '', checked: false, dataset: {},
            addEventListener(type, callback) { (listeners[type] ??= []).push(callback); },
            dispatchEvent(event) { for (const callback of listeners[event.type] || []) callback(event); },
            click() { this.dispatchEvent({ type: 'click' }); },
            setAttribute() {},
        };
    }
    const search = element();
    const category = element();
    const tag = element('7');
    const clearTags = element();
    const clear = element();
    const all = element();
    all.addEventListener('click', () => { category.value = ''; });
    clearTags.addEventListener('click', () => { tag.checked = false; });
    const status = element();
    const grid = element();
    grid.dataset.filterUrl = '/products/filter/';
    grid.querySelectorAll = () => [];
    const panel = {
        querySelectorAll(selector) {
            if (selector === '[data-category]') return [all];
            if (selector === 'input[type="search"]') return [search];
            return selector.includes(':checked') ? (tag.checked ? [tag] : []) : [tag];
        },
        querySelector: () => all,
    };
    const ids = { search, 'category-value': category, 'product-grid': grid,
        'filter-status': status, 'clear-tags': clearTags, 'clear-filters': clear };
    const requests = [];
    const timers = new Map();
    let nextTimer = 0;
    const context = vm.createContext({
        document: { querySelector: () => panel, getElementById: (id) => ids[id] },
        URLSearchParams, AbortController, Event,
        setTimeout(callback, delay) { timers.set(++nextTimer, { callback, delay }); return nextTimer; },
        clearTimeout(id) { timers.delete(id); },
        fetch(url, options) { return new Promise((resolve, reject) => requests.push({ url, ...options, resolve, reject })); },
        disposeProductCards() {}, initializeProductCards() { return () => {}; },
    });
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../static/products/filters.js'), 'utf8'), context);
    return { search, category, tag, clear, clearTags, grid, status, requests, timers,
        flush() { const pending = [...timers.values()]; timers.clear(); pending.forEach(({ callback }) => callback()); } };
}
const input = (element) => element.dispatchEvent({ type: 'input' });
const change = (element) => element.dispatchEvent({ type: 'change' });
const settle = () => new Promise((resolve) => setImmediate(resolve));

test('typing is debounced and sends the latest search', () => {
    const s = setup();
    s.search.value = 'la'; input(s.search);
    s.search.value = 'lamp'; input(s.search);
    assert.equal(s.requests.length, 0);
    assert.equal(s.timers.size, 1);
    assert.equal([...s.timers.values()][0].delay, 300);
    s.flush();
    assert.equal(s.requests[0].url, '/products/filter/?search=lamp');
});

test('tag select/deselect sends IDs and clear resets all with one request', () => {
    const s = setup();
    s.category.value = '2'; s.tag.checked = true; change(s.tag);
    assert.equal(s.requests[0].url, '/products/filter/?categoryId=2&tagIds=7');
    s.tag.checked = false; change(s.tag);
    assert.equal(s.requests[1].url, '/products/filter/?categoryId=2');
    s.search.value = 'lamp'; input(s.search);
    s.clear.click();
    assert.equal(s.requests.length, 3);
    assert.equal(s.requests[2].url, '/products/filter/?');
    assert.equal(s.timers.size, 0);
    assert.equal(s.category.value, '');
    assert.equal(s.search.value, '');
});

test('new input aborts immediately and stale responses never replace new results', async () => {
    const s = setup();
    change(s.tag);
    const old = s.requests[0];
    s.search.value = 'new'; input(s.search);
    assert.equal(old.signal.aborted, true);
    s.flush();
    s.requests[1].resolve({ ok: true, text: async () => 'NEW' });
    await settle();
    old.resolve({ ok: true, text: async () => 'OLD' });
    await settle();
    assert.equal(s.grid.innerHTML, 'NEW');
});

test('failed request keeps existing results and clear can retry', async () => {
    const s = setup();
    s.grid.innerHTML = 'EXISTING';
    change(s.tag);
    s.requests[0].resolve({ ok: false });
    await settle();
    assert.equal(s.grid.innerHTML, 'EXISTING');
    assert.match(s.status.textContent, /Could not load products/);
    s.clear.click();
    assert.equal(s.requests.length, 2);
});
