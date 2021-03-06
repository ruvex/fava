import { select, selectAll, once } from "./helpers";
import e from "./events";
import { closeOverlay } from "./stores";

/**
 * Add a tooltip showing the keyboard shortcut over the target element.
 */
function showTooltip(target: HTMLElement): void {
  const tooltip = document.createElement("div");
  tooltip.className = "keyboard-tooltip";
  tooltip.innerHTML = target.getAttribute("data-key") || "";
  document.body.appendChild(tooltip);
  const parentCoords = target.getBoundingClientRect();
  // Padded 10px to the left if there is space or centered otherwise
  const left =
    parentCoords.left +
    Math.min((target.offsetWidth - tooltip.offsetWidth) / 2, 10);
  const top =
    parentCoords.top + (target.offsetHeight - tooltip.offsetHeight) / 2;
  tooltip.style.left = `${left}px`;
  tooltip.style.top = `${top + window.pageYOffset}px`;
}

/**
 * Show all keyboard shortcut tooltips.
 */
function showTooltips(): void {
  const reloadButton = select("#reload-page");
  if (reloadButton) {
    reloadButton.classList.remove("hidden");
  }
  selectAll("[data-key]").forEach(el => {
    showTooltip(el as HTMLElement);
  });
}

/**
 * Remove all keyboard shortcut tooltips.
 */
function removeTooltips(): void {
  const reloadButton = select("#reload-page");
  if (reloadButton) {
    reloadButton.classList.add("hidden");
  }
  selectAll(".keyboard-tooltip").forEach(tooltip => {
    tooltip.remove();
  });
}

/**
 * Ignore events originating from editable elements.
 */
function editableElement(element: EventTarget | null): boolean {
  return (
    element instanceof HTMLElement &&
    (element.tagName === "INPUT" ||
      element.tagName === "SELECT" ||
      element.tagName === "TEXTAREA" ||
      element.isContentEditable)
  );
}

type KeyboardEventHandler = (event: KeyboardEvent) => void;
const keyboardShortcuts: Record<string, KeyboardEventHandler> = {};
// The last typed character to check for sequences of two keys.
let lastChar = "";

/**
 * Handle a `keydown` event on the document.
 *
 * Dispatch to the relevant handler.
 */
function keydown(event: KeyboardEvent): void {
  if (editableElement(event.target)) {
    // ignore events in editable elements.
    return;
  }
  let eventKey = event.key;
  if (event.metaKey) {
    eventKey = `Meta+${eventKey}`;
  }
  if (event.altKey) {
    eventKey = `Alt+${eventKey}`;
  }
  if (event.ctrlKey) {
    eventKey = `Control+${eventKey}`;
  }
  const lastTwoKeys = `${lastChar} ${eventKey}`;
  if (lastTwoKeys in keyboardShortcuts) {
    keyboardShortcuts[lastTwoKeys](event);
  } else if (eventKey in keyboardShortcuts) {
    keyboardShortcuts[eventKey](event);
  }
  if (event.key !== "Alt" && event.key !== "Control" && event.key !== "Shift") {
    lastChar = eventKey;
  }
}

document.addEventListener("keydown", keydown);

/**
 * Bind an event handler to a key.
 */
function bind(key: string, handler: KeyboardEventHandler): void {
  const sequence = key.split(" ");
  if (sequence.length > 2) {
    // eslint-disable-next-line no-console
    console.error("Only key sequences of length <=2 are supported: ", key);
  }
  if (key in keyboardShortcuts) {
    // eslint-disable-next-line no-console
    console.error("Duplicate keyboard shortcut: ", key);
  }
  keyboardShortcuts[key] = handler;
}

function unbind(key: string): void {
  delete keyboardShortcuts[key];
}

export const keys = {
  bind,
  unbind,
};

/**
 * A svelte action to attach a global keyboard shortcut.
 *
 * This will attach a listener for the given key (or key sequence of length 2).
 * This listener will focus the given node if it is an <input> element and
 * trigger a click on it otherwise.
 */
export function keyboardShortcut(
  node: HTMLElement,
  key?: string
): { destroy?: () => void } {
  if (!key) {
    return {};
  }
  node.setAttribute("data-key", key);
  bind(key, event => {
    if (node.tagName === "INPUT") {
      event.preventDefault();
      (node as HTMLInputElement).focus();
    } else {
      node.click();
    }
  });

  return {
    destroy(): void {
      unbind(key);
    },
  };
}

let currentShortcuts: string[] = [];
e.on("page-loaded", () => {
  currentShortcuts.map(unbind);
  currentShortcuts = [];
  selectAll("[data-key]").forEach(element => {
    const key = element.getAttribute("data-key");
    if (key !== null && !(key in keyboardShortcuts)) {
      currentShortcuts.push(key);
      bind(key, () => {
        const tag = element.tagName;
        if (tag === "BUTTON" || tag === "A") {
          (element as HTMLButtonElement | HTMLAnchorElement).click();
        } else if (tag === "INPUT") {
          (element as HTMLInputElement).focus();
        }
      });
    }
  });
});

e.on("page-init", () => {
  bind("?", () => {
    showTooltips();
    once(document, "mousedown", () => {
      removeTooltips();
    });
    once(document, "keydown", () => {
      removeTooltips();
    });
  });

  bind("Escape", closeOverlay);
});
