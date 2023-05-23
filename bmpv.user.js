// ==UserScript==
// @name         bmpv
// @namespace    sora.zip
// @version      0.1
// @description  play bilibili video in mpv
// @author       CrackTC
// @match        https://www.bilibili.com/video/*
// @match        https://www.bilibili.com/bangumi/play/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

async function get_player() {
    if (typeof player === "undefined" || player.isPaused() === true) {
        await sleep(500);
        return await get_player();
    }
    else {
        return player;
    }
}

function get_url() {
    return document.location.toString();
}

async function play() {
    'use strict';
    var player = await get_player();
    var url = `bmpv://localhost/?url=${encodeURIComponent(get_url())}&cid=${player.getManifest().cid}`;
    console.info("bmpv: " + url);
    window.location.href = url;
    player.disconnect();
};

play();

var tmp = history.pushState;
history.pushState = function (a, b, c) {
    tmp(a, b, c);
    play();
}
