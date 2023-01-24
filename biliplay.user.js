// ==UserScript==
// @name         biliplay
// @namespace    cracktc.top
// @version      0.1
// @description  play bilibili video in mpv
// @author       CrackTC
// @match        https://www.bilibili.com/video/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

function sleep (time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}

async function get_cid() {
    if (typeof cid === "undefined") {
        await sleep(500);
        return get_cid();
    }
    else {
        return cid;
    }
}

async function get_player() {
    if (typeof player === "undefined" || player.isPaused() === true) {
        await sleep(500);
        return get_player();
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

    var url = `bmpv://localhost/?url=${encodeURIComponent(get_url())}&cid=${window.__INITIAL_STATE__.videoData.pages[0].cid}`;
    console.log("bmpv: " + url);
    window.location.href = url;
    (await get_player()).disconnect();
};

play();

var tmp = history.pushState;
history.pushState = function (a,b,c) {
    tmp(a,b,c);
    play();
}