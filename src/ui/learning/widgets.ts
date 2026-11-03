import type { WidgetDef } from './types';
import type { WidgetApi } from './widgetKit';
import { advantageMatcher, connectThreads, needSorter, networkSizeChooser, tapToClassify } from './widgetsA';
import { atmToy, clientServerToy, p2pVsCsToy } from './widgetsB';

export type { WidgetApi };

/** Mounts the widget for a step and returns its cleanup. */
export function mountWidget(def: WidgetDef, host: HTMLElement, api: WidgetApi): () => void {
  switch (def.type) {
    case 'connect_threads': return connectThreads(host, def.spec, api);
    case 'tap_to_classify': return tapToClassify(host, def.spec, api);
    case 'network_size_chooser': return networkSizeChooser(host, def.spec, api);
    case 'advantage_matcher': return advantageMatcher(host, def.spec, api);
    case 'client_server_toy': return clientServerToy(host, def.spec, api);
    case 'atm_toy': return atmToy(host, def.spec, api);
    case 'p2p_vs_cs_toy': return p2pVsCsToy(host, def.spec, api);
    case 'need_sorter': return needSorter(host, def.spec, api);
  }
}

export { connectThreads, tapToClassify, networkSizeChooser, advantageMatcher, clientServerToy, atmToy, p2pVsCsToy, needSorter };
