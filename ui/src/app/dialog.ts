import { SlButton } from '@shoelace-style/shoelace';

export function escapeHtml(html) {
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
}

export async function alertDialog(label: string, message: string, button_text = 'Ok', variant = 'primary'): Promise<void> {
  // create the dialog
  const dialog = Object.assign(document.createElement('sl-dialog'), {
    variant: variant,
    label: label,
    innerHTML: `
        ${escapeHtml(message)}
        <sl-button class="cancel" slot="footer"}>Cancel</sl-button>
        <sl-button class="accept" variant=${variant} slot="footer" style="margin-left: 2rem">${button_text}</sl-button>`,
  });
  document.body.appendChild(dialog);
  try {
    dialog.show();
  } catch (TypeError) {
    // throws this error but works correctly (unlike open attribute)
  }
  // wait for the user to click a button
  return new Promise<void>((resolve) => {
    dialog.addEventListener('click', (_) => {
      document.body.removeChild(dialog);
      resolve();
    });
  });
}

export async function confirmDialog(label: string, message: string, button_text = 'Ok', variant = 'primary'): Promise<boolean> {
  // create the dialog
  const dialog = Object.assign(document.createElement('sl-dialog'), {
    variant: variant,
    label: label,
    innerHTML: `
        ${escapeHtml(message)}
        <sl-button class="cancel" slot="footer"}>Cancel</sl-button>
        <sl-button class="accept" variant=${variant} slot="footer" style="margin-left: 2rem">${button_text}</sl-button>`,
  });
  document.body.appendChild(dialog);
  try {
    dialog.show();
  } catch (TypeError) {
    // throws this error but works correctly (unlike open attribute)
  }
  // wait for the user to click a button
  return new Promise<boolean>((resolve) => {
    dialog.addEventListener('click', (event) => {
      document.body.removeChild(dialog);
      resolve((event.target as SlButton).className === 'accept');
    });
  });
}

export async function promptDialog(label: string, input_param = {}): Promise<string> {
  const dialog = Object.assign(document.createElement('sl-dialog'), {
    variant: 'primary',
    label: label,
    innerHTML: `
        <div id="in"></div>
        <sl-button class="cancel" slot="footer"}>Cancel</sl-button>
        <sl-button class="accept" variant="primary" slot="footer" style="margin-left: 2rem">Ok</sl-button>`,
  });
  const input = Object.assign(document.createElement('sl-input'), input_param);
  dialog.querySelector('#in').appendChild(input);
  document.body.appendChild(dialog);
  try {
    dialog.show();
  } catch (TypeError) {
    // throws this error but works correctly (unlike open attribute)
  }
  // wait for the user to click a button or close the dialog
  return new Promise<string>(async (resolve) => {
    const accept = dialog.querySelector('.accept') as SlButton;
    const cancel = dialog.querySelector('.cancel') as SlButton;
    accept.addEventListener('click', (_) => {
      if (input.validity.valid) {
        document.body.removeChild(dialog);
        resolve(input.value);
      } else {
        alertDialog('Invalid Input', input.validationMessage);
      }
    });
    cancel.addEventListener('click', (_) => {
      document.body.removeChild(dialog);
      resolve(undefined);
    });
    dialog.addEventListener('sl-hide', (_) => {
      document.body.removeChild(dialog);
      resolve(undefined);
    });
  });
}
