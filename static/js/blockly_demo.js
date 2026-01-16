(function () {
  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function showMsg(type, text) {
    const el = qs('#demoMsg');
    if (!el) return;
    el.innerHTML = '';
    const div = document.createElement('div');
    div.className = 'alert ' + type;
    div.textContent = text;
    el.appendChild(div);
  }

  const blocklyArea = qs('#blocklyArea');
  const codeTextarea = qs('#codeTextarea');
  const runBtn = qs('#runBtn');
  const copyBtn = qs('#copyBtn');

  if (!blocklyArea || !codeTextarea) {
    return;
  }

  if (!window.Blockly || !window.CodeMirror) {
    showMsg('error', 'Failed to load Blockly or CodeMirror. Check your internet connection.');
    return;
  }

  // Toolbox closely matches Blockly demo categories.
  const toolbox = {
    kind: 'categoryToolbox',
    contents: [
      {
        kind: 'category',
        name: 'Logic',
        categorystyle: 'logic_category',
        contents: [
          { kind: 'block', type: 'controls_if' },
          { kind: 'block', type: 'logic_compare' },
          { kind: 'block', type: 'logic_operation' },
          { kind: 'block', type: 'logic_boolean' },
          { kind: 'block', type: 'logic_negate' },
          { kind: 'block', type: 'logic_null' },
        ],
      },
      {
        kind: 'category',
        name: 'Loops',
        categorystyle: 'loop_category',
        contents: [
          { kind: 'block', type: 'controls_whileUntil' },
          { kind: 'block', type: 'controls_flow_statements' },
        ],
      },
      {
        kind: 'category',
        name: 'Math',
        categorystyle: 'math_category',
        contents: [
          { kind: 'block', type: 'math_number' },
          { kind: 'block', type: 'math_arithmetic' },
          { kind: 'block', type: 'math_round' },
        ],
      },
      {
        kind: 'category',
        name: 'Text',
        categorystyle: 'text_category',
        contents: [
          { kind: 'block', type: 'text' },
          { kind: 'block', type: 'text_print' },
          { kind: 'block', type: 'text_join' },
          { kind: 'block', type: 'text_length' },
        ],
      },
      {
        kind: 'category',
        name: 'Lists',
        categorystyle: 'list_category',
        contents: [
          { kind: 'block', type: 'lists_create_with' },
          { kind: 'block', type: 'lists_length' },
          { kind: 'block', type: 'lists_getIndex' },
          { kind: 'block', type: 'lists_setIndex' },
        ],
      },
      { kind: 'category', name: 'Variables', custom: 'VARIABLE' },
      { kind: 'category', name: 'Functions', custom: 'PROCEDURE' },
    ],
  };

  const workspace = Blockly.inject(blocklyArea, {
    toolbox,
    rtl: false,
    scrollbars: true,
    trashcan: true,
  });

  // Code editor (CodeMirror)
  const editor = CodeMirror.fromTextArea(codeTextarea, {
    mode: 'python',
    lineNumbers: true,
    readOnly: true,
    viewportMargin: Infinity,
  });

  function setCode(code) {
    editor.setValue(code || '');
  }

  function safePythonCode() {
    try {
      if (!Blockly.Python || !Blockly.Python.workspaceToCode) {
        return '# Python generator not loaded.';
      }
      return Blockly.Python.workspaceToCode(workspace) || '';
    } catch {
      return '# Error generating Python.';
    }
  }

  function updateCode() {
    setCode(safePythonCode());
  }

  workspace.addChangeListener(updateCode);

  // Default example: alo = 1; while alo <= 3: print("Hello World!"); alo = alo + 1
  const defaultXml = `
<xml xmlns="https://developers.google.com/blockly/xml">
  <variables>
    <variable id="alo">alo</variable>
  </variables>
  <block type="variables_set" id="set1" x="20" y="20">
    <field name="VAR" id="alo">alo</field>
    <value name="VALUE">
      <block type="math_number" id="num1">
        <field name="NUM">1</field>
      </block>
    </value>
    <next>
      <block type="controls_whileUntil" id="while1">
        <field name="MODE">WHILE</field>
        <value name="BOOL">
          <block type="logic_compare" id="cmp1">
            <field name="OP">LTE</field>
            <value name="A">
              <block type="variables_get" id="get1">
                <field name="VAR" id="alo">alo</field>
              </block>
            </value>
            <value name="B">
              <block type="math_number" id="num3">
                <field name="NUM">3</field>
              </block>
            </value>
          </block>
        </value>
        <statement name="DO">
          <block type="text_print" id="print1">
            <value name="TEXT">
              <block type="text" id="txt1">
                <field name="TEXT">Hello World!</field>
              </block>
            </value>
            <next>
              <block type="variables_set" id="set2">
                <field name="VAR" id="alo">alo</field>
                <value name="VALUE">
                  <block type="math_arithmetic" id="add1">
                    <field name="OP">ADD</field>
                    <value name="A">
                      <block type="variables_get" id="get2">
                        <field name="VAR" id="alo">alo</field>
                      </block>
                    </value>
                    <value name="B">
                      <block type="math_number" id="numInc">
                        <field name="NUM">1</field>
                      </block>
                    </value>
                  </block>
                </value>
              </block>
            </next>
          </block>
        </statement>
      </block>
    </next>
  </block>
</xml>`;

  try {
    workspace.clear();
    const dom = Blockly.Xml.textToDom(defaultXml);
    Blockly.Xml.domToWorkspace(dom, workspace);
  } catch {
    // ignore
  }

  updateCode();

  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(editor.getValue() || '');
        showMsg('success', 'Copied.');
      } catch {
        showMsg('warn', 'Copy failed.');
      }
    });
  }

  if (runBtn) {
    runBtn.addEventListener('click', () => {
      showMsg('warn', 'Run is a stub (frontend-only). You can copy the Python code for now.');
    });
  }
})();
