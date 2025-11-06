// ==UserScript==
// @name         Сборщик слов с Quizlet
// @namespace    Dimka's Realm
// @version      0.8
// @description  Собирает пары терминов Quizlet и сохраняет их в CSV с названием набора без "Quizlet" в имени файла, в формате №;Español;Русский с UTF-8 BOM для Excel.
// @author       You
// @match        https://quizlet.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const selector = '.s16qqoff';
    const collected = new Map();

    // Получаем название набора
    let rawTitle = document.title || 'quizlet_terms';
    let cleanTitle = rawTitle.replace(/\s*\|\s*Quizlet/i, '').trim();

    // Создаём UI
    const panel = document.createElement('div');
    panel.style.position = 'fixed';
    panel.style.top = '10px';
    panel.style.right = '10px';
    panel.style.width = '420px';
    panel.style.maxHeight = '80vh';
    panel.style.overflow = 'hidden';
    panel.style.zIndex = '9999';
    panel.style.background = '#f9f9f9';
    panel.style.border = '1px solid #ccc';
    panel.style.borderRadius = '8px';
    panel.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
    panel.style.fontFamily = 'Arial, sans-serif';
    panel.style.padding = '10px';

    panel.innerHTML = `
        <h3 style="margin-top:0;">📚 ${cleanTitle}</h3>
        <p id="term-count">Собрано: 0 пар</p>
        <div style="overflow-y:auto; max-height:300px; border:1px solid #ddd; background:#fff;">
            <table id="term-table" style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr>
                        <th style="border-bottom:1px solid #ccc; text-align:left; padding:4px;">№</th>
                        <th style="border-bottom:1px solid #ccc; text-align:left; padding:4px;">Español</th>
                        <th style="border-bottom:1px solid #ccc; text-align:left; padding:4px;">Русский</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        <button id="download-btn" style="margin-top:10px; padding:5px 10px;">💾 Сохранить CSV</button>
    `;
    document.body.appendChild(panel);

    const countEl = document.getElementById('term-count');
    const tableBody = panel.querySelector('#term-table tbody');
    const downloadBtn = document.getElementById('download-btn');

    function updateUI() {
        countEl.textContent = `Собрано: ${collected.size} пар`;
        tableBody.innerHTML = '';
        Array.from(collected.entries()).forEach(([original, translation], index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="border-bottom:1px solid #eee; padding:4px;">${index + 1}</td>
                <td style="border-bottom:1px solid #eee; padding:4px;">${original}</td>
                <td style="border-bottom:1px solid #eee; padding:4px;">${translation}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    setInterval(() => {
        const cards = document.querySelectorAll(selector);
        let added = 0;

        cards.forEach(card => {
            const sides = card.querySelectorAll('[data-testid="set-page-term-card-side"]');
            if (sides.length >= 1) {
                const original = sides[0].innerText.trim();
                const translation = sides.length >= 2 ? sides[1].innerText.trim() : ' ';
                if (original && !collected.has(original)) {
                    collected.set(original, translation || ' ');
                    added++;
                }
            }
        });

        if (added > 0) updateUI();
    }, 1000);

    downloadBtn.addEventListener('click', () => {
        let csv = '№;Español;Русский\n';
        Array.from(collected.entries()).forEach(([original, translation], index) => {
            csv += `${index + 1};"${original.replace(/"/g, '""')}";"${translation.replace(/"/g, '""')}"\n`;
        });

        const BOM = '\uFEFF';
        const blob = new Blob([BOM + csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${cleanTitle}.csv`;
        link.click();
    });
})();